import geopandas as gpd
import osmnx as ox
import pandas as pd
import pytest
from shapely.geometry import LineString, Point

from gpbp.distance import (
    calculate_isopolygons_graph,
    create_polygon_from_nodes_and_edges,
)


@pytest.fixture
def nodes_gdf() -> gpd.GeoSeries:
    data = {
        "osmid": [5909483619, 5909483625, 5909483636],
        "geometry": [
            Point(-122.2314069, 37.7687054),
            Point(-122.231243, 37.7687576),
            Point(-122.2317839, 37.7689584),
        ],
    }

    return gpd.GeoDataFrame(data, crs="EPSG:4326").set_index("osmid")


@pytest.fixture
def edges_gdf() -> gpd.GeoSeries:
    coordinates_25_to_19 = [(-122.23124, 37.76876), (-122.23141, 37.76871)]

    coordinates_19_to_36 = [
        (-122.2314069, 37.7687054),
        (-122.2314797, 37.7687656),
        (-122.2315618, 37.7688239),
        (-122.2316698, 37.7688952),
        (-122.2317839, 37.7689584),
    ]

    return gpd.GeoSeries(
        [
            LineString(coordinates_25_to_19),  # edge 5909483625 -> 5909483619
            LineString(coordinates_25_to_19[::-1]),  # edge 5909483619 -> 5909483625
            LineString(coordinates_19_to_36),  # edge 5909483619 -> 5909483636
            LineString(coordinates_19_to_36[::-1]),  # edge 5909483636 -> 5909483619
        ],
        crs="EPSG:4326",
    )


@pytest.fixture
def excluded_node() -> Point:
    """Geometry of the node 5909483569"""
    return Point(-122.2315948, 37.768278)


@pytest.fixture
def dataframe_with_lat_and_lon() -> pd.DataFrame:

    points = [
        (-122.2314069, 37.7687054),  # closest node 19
        (-122.23124, 37.76876),  # closest node 25
    ]

    return pd.DataFrame(points, columns=["longitude", "latitude"])


class TestCreatePolygonFromNodesAndEdges:

    def test_excluded_node_is_left_out(self, nodes_gdf, edges_gdf, excluded_node):
        """Desired behavior: the node previously excluded because it was
        too far away is excluded from the resulting polygon"""

        poly = create_polygon_from_nodes_and_edges(
            nodes_gdf=nodes_gdf,
            edges_gdf=edges_gdf,
            node_buff=0.00005,
            edge_buff=0.00005,
        )

        assert not poly.contains(excluded_node)

    def test_excluded_node_is_back_in(self, nodes_gdf, edges_gdf, excluded_node):
        """Undesired behavior: the node previously excluded because it was
        too far away is included in the resulting polygon. The problem is
        that buffers are too large"""

        poly = create_polygon_from_nodes_and_edges(
            nodes_gdf=nodes_gdf, edges_gdf=edges_gdf
        )

        assert poly.contains(excluded_node)

    def test_with_0_node_buffer(self, nodes_gdf, edges_gdf):
        """This should not be a problem because all nodes are connected"""

        poly = create_polygon_from_nodes_and_edges(
            nodes_gdf=nodes_gdf, edges_gdf=edges_gdf, node_buff=0, edge_buff=0.00005
        )

        assert poly.area > 0


class TestCalculateIsopolygonsGraph:

    @pytest.fixture(autouse=True)
    def setup(
        self,
        dataframe_with_lat_and_lon,
    ):
        """
        Here I'm deliberately choosing to override the defaults for node_buff and edge_buff
        so the tests pass, otherwise the tests would fail because the buffers are too large
        """

        self.isopolygons = calculate_isopolygons_graph(
            facilities_df=dataframe_with_lat_and_lon,
            distance_type="length",
            distance_values=[5, 20, 50],
            road_network=ox.load_graphml(
                "tests/test_data/walk_network_4_nodes_6_edges.graphml"
            ),
            node_buff=0.00005,
            edge_buff=0.00005,
        )

    def test_format(self):

        assert self.isopolygons.shape == (
            2,
            3,
        ), "The output should have two rows (one per point in input dataframe) and three columns (one per distance)"

        assert list(self.isopolygons.columns) == ["ID_5", "ID_20", "ID_50"]

    def test_nodes_in_isopolygon_5(self, nodes_gdf):
        """Nodes in isopolygon at distance 5 meters from point (-122.2314069, 37.7687054)"""

        assert list(nodes_gdf.geometry.within(self.isopolygons.loc[0, "ID_5"])) == [
            True,
            False,
            False,
        ], "The only node in this isopolygon should be 5909483619"

    def test_nodes_in_isopolygon_20(self, nodes_gdf):
        """Nodes in isopolygon at distance 20 meters from point (-122.2314069, 37.7687054)"""

        assert list(nodes_gdf.geometry.within(self.isopolygons.loc[0, "ID_20"])) == [
            True,
            True,
            False,
        ], "Only two nodes, 5909483619 and 5909483625, should be in this isopolygon"

    def test_nodes_in_isopolygon_50(self, nodes_gdf, excluded_node):
        """Nodes in isopolygon at distance 50 meters from point (-122.2314069, 37.7687054)"""

        assert all(
            nodes_gdf.geometry.within(self.isopolygons.loc[0, "ID_50"])
        ), "Nodes 5909483619, 5909483625 and 5909483636 should be in this isopolygon"

        assert not excluded_node.within(
            self.isopolygons.loc[0, "ID_50"]
        ), "Node 5909483569 should not be in this isopolygon"
