"""
For now we are only implementing OSM. In the future can be extended to geojson
or other sources
"""

from dataclasses import dataclass, field

from geopandas import GeoDataFrame
from shapely import MultiPolygon, Polygon


@dataclass
class Facilities:
    """Only OSM facilities now!"""

    # can't define class default with mutable paramenter (tags which is a dictionary).
    # here fixed w default_factory, but could be done differently

    admin_area_boundaries: Polygon | MultiPolygon
    data_src: str = "osm"
    tags: dict = field(
        default_factory=lambda: {"building": "hospital"}
    )  # we think this default should change, awaiting Joaquim's response

    def get_existing_facilities(self) -> GeoDataFrame:
        """Get facilities from OSM"""
        ...

    @staticmethod
    def estimate_potential_facilities() -> GeoDataFrame:
        "can probably be static method"
        ...
