import geopandas as gpd
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


class TestCalculateIsopolygonsGraph:

    @pytest.mark.parametrize(
        "load_graphml_file",
        ["tests/test_data/walk_network_4_nodes_6_edges.graphml"],
        indirect=True,
    )
    def test_one(self, load_graphml_file):
        """

        # point closest to node 19? I got it like so:
        #
        # line = LineString(coordinates_25_to_19[::-1])
        # a_point_in_line = line_interpolate_point(line, 5)

        # print(a_point_in_line)

        # line_interpolate_point(line, 5)
        #
        # print(a_point_in_line)

        """

        # x = -122.23124
        # y = 37.76876

        x = -122.2314069
        y = 37.7687054

        # this point should lie in the edge between 19 and 25, and should be around 5m away from node 19
        # a_point = Point(-122.23124, 37.76876)  # closest node 25
        another_point = Point(
            -122.2314069, 37.7687054
        )  # print(line_interpolate_point(line_19_36, 5))

        G = load_graphml_file

        isopolygons = calculate_isopolygons_graph(
            X=x,
            Y=y,
            distance_type="length",
            distance_values=[20],
            road_network=G,
            node_buff=0.00005,
            edge_buff=0.00005,
        )

        assert set(isopolygons.keys()) == {"ID_20"}

        # assert nodes 19 and 25 are in the isopolygon, but the other two are not as they are farther away than 20 meters

        isopolygon_20 = isopolygons["ID_20"]

        assert isopolygon_20.contains(
            Point(-122.2314069, 37.7687054)
        )  # node 19 should be in

        assert isopolygon_20.contains(another_point)  # the point itself should be in

        assert not isopolygon_20.contains(
            Point(-122.2317839, 37.7689584)
        )  # node 36 should not be in

    @pytest.mark.parametrize(
        "load_graphml_file",
        ["tests/test_data/walk_network_4_nodes_6_edges.graphml"],
        indirect=True,
    )
    def test_two(self, load_graphml_file):

        x = -122.2314069
        y = 37.7687054

        another_point = Point(
            -122.2314069, 37.7687054
        )  # print(line_interpolate_point(line_19_36, 5))

        G = load_graphml_file

        isopolygons = calculate_isopolygons_graph(
            X=x,
            Y=y,
            distance_type="length",
            distance_values=[50],
            road_network=G,
            node_buff=0.00005,
            edge_buff=0.00005,
        )

        assert isopolygons["ID_50"].contains(
            Point(-122.2317839, 37.7689584)
        )  # contains node 36

    @pytest.mark.parametrize(
        "load_graphml_file",
        ["tests/test_data/walk_network_4_nodes_6_edges.graphml"],
        indirect=True,
    )
    def test_three(self, load_graphml_file):

        points = gpd.GeoDataFrame(
            [
                Point(
                    -122.2314069, 37.7687054
                ),  # print(line_interpolate_point(line_19_36, 5)). closest node 19
                Point(-122.23124, 37.76876),  # closest node 25
            ]
        )

        G = load_graphml_file

        isopolygons = calculate_isopolygons_graph(
            X=x,
            Y=y,
            distance_type="length",
            distance_values=[5, 20, 50],
            road_network=G,
            node_buff=0.00005,
            edge_buff=0.00005,
        )

        assert isopolygons.shape == (2, 3)  # three rows and two columns, one per node

        isopolygons.loc[0, "ID_5"]
