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
def excluded_node():
    return Point(-122.2315948, 37.768278)


class TestCreatePolygonFromNodesAndEdges:

    def test_excluded_node_is_left_out(self, nodes_gdf, edges_gdf, excluded_node):
        """Desired behavior: the node previously excluded because it was
        too far away is excluded from the resulting polygon"""

        poly = create_polygon_from_nodes_and_edges(
            node_buff=0.00005,
            edge_buff=0.00005,
            nodes_gdf=nodes_gdf,
            edges_gdf=edges_gdf,
        )

        assert not poly.contains(excluded_node)

    def test_excluded_node_is_back_in(self, nodes_gdf, edges_gdf, excluded_node):
        """Undesired behavior: the node previously excluded because it was
        too far away is included in the resulting polygon. The problem is
        that buffers are too large"""

        poly = create_polygon_from_nodes_and_edges(
            node_buff=0.001, edge_buff=0.0005, nodes_gdf=nodes_gdf, edges_gdf=edges_gdf
        )

        assert poly.contains(excluded_node)

    def test_with_0_node_buffer(self, nodes_gdf, edges_gdf):
        """This should not be a problem because all nodes are connected"""

        poly = create_polygon_from_nodes_and_edges(
            node_buff=0, edge_buff=0.00005, nodes_gdf=nodes_gdf, edges_gdf=edges_gdf
        )

        assert poly.area > 0


@pytest.fixture
def dataframe_with_lat_and_lon() -> pd.DataFrame:
    """Here is how I got the first point:

    I created a Linestring between nodes 19 and 36:
    line_19_36 = LineString([[-122.2317839, 37.7689584],[-122.2314069, 37.7687054]])

    From Shapely 2.0.6 docs: returns a point interpolated at given distance on a line
    print(line_interpolate_point(line_19_36, 5))

    The second was done similarly.

    """

    points = [
        (-122.2314069, 37.7687054),  # closest node 19
        (-122.23124, 37.76876),  # closest node 25
    ]

    return pd.DataFrame(points, columns=["longitude", "latitude"])


class TestCalculateIsopolygonsGraph:

    @pytest.mark.parametrize(
        "load_graphml_file",
        ["tests/test_data/walk_network_4_nodes_6_edges.graphml"],
        indirect=True,
    )
    def test_three(
        self, load_graphml_file, dataframe_with_lat_and_lon, nodes_gdf, excluded_node
    ):

        G = load_graphml_file

        isopolygons = calculate_isopolygons_graph(
            X=dataframe_with_lat_and_lon.longitude.to_list(),
            Y=dataframe_with_lat_and_lon.latitude.to_list(),
            distance_type="length",
            distance_values=[5, 20, 50],
            road_network=G,
            node_buff=0.00005,
            edge_buff=0.00005,
        )

        assert isopolygons.shape == (2, 3)  # three rows and two columns, one per node

        assert list(isopolygons.columns) == ["ID_5", "ID_20", "ID_50"]

        # the only node in this isopolygon is 19
        assert list(nodes_gdf.geometry.within(isopolygons.loc[0, "ID_5"])) == [
            True,
            False,
            False,
        ]

        # both nodes 19 and 25 are in this isopolygon, but not 36
        assert list(nodes_gdf.geometry.within(isopolygons.loc[0, "ID_20"])) == [
            True,
            True,
            False,
        ]

        # nodes 19, 25 and 36 are in this isopolygon
        assert all(nodes_gdf.geometry.within(isopolygons.loc[0, "ID_50"]))

        # node 69 is not in this isopolygon
        assert not excluded_node.within(isopolygons.loc[0, "ID_50"])
