import pytest
import geopandas as gpd
from shapely.geometry import Point, LineString
from gpbp.distance import create_polygon_from_nodes_and_edges


@pytest.fixture
def nodes_gdf():
    nodes_gdf_data = {
        "id": [5909483619, 5909483625, 5909483636],
        "geometry": [
            Point(-122.2314069, 37.7687054),
            Point(-122.231243, 37.7687576),
            Point(-122.2317839, 37.7689584),
        ],
    }

    return gpd.GeoDataFrame(
        nodes_gdf_data,
    ).set_index("id")


@pytest.fixture
def edges_gdf():
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
        ]
    )


@pytest.fixture
def excluded_node():
    return Point(-122.2315948, 37.768278)


def test_excluded_node_is_left_out(nodes_gdf, edges_gdf, excluded_node):
    """Desired behavior: the node previously excluded because it was
    too far away is excluded from the resulting polygon"""

    poly = create_polygon_from_nodes_and_edges(
        node_buff=0.00005, edge_buff=0.00005, nodes_gdf=nodes_gdf, edges_gdf=edges_gdf
    )

    assert not poly.contains(excluded_node)


def test_excluded_node_is_back_in(nodes_gdf, edges_gdf, excluded_node):
    """Undesired behavior: the node previously excluded because it was
    too far away is included in the resulting polygon. The problem is
    that buffers are too large"""

    poly = create_polygon_from_nodes_and_edges(
        node_buff=0.001, edge_buff=0.0005, nodes_gdf=nodes_gdf, edges_gdf=edges_gdf
    )

    assert poly.contains(excluded_node)


def test_with_0_node_buffer(nodes_gdf, edges_gdf):
    """This should not be a problem because all nodes are connected"""

    poly = create_polygon_from_nodes_and_edges(
        node_buff=0, edge_buff=0.00005, nodes_gdf=nodes_gdf, edges_gdf=edges_gdf
    )

    assert poly.area > 0
