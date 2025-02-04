from typing import Optional

import pycountry
from gadm import GADMDownloader
from geopandas import GeoDataFrame
from shapely import MultiPolygon, Polygon


class AdministrativeArea:
    """Only meant to have administrative fields (e.g. name)
    and geometry (the boundaries of the administrative area )"""

    def __init__(
        self,
        country_name: str,
        admin_level: int,
        admin_area_name: Optional[
            str
        ],  # if known can be set directly. Good idea, bad idea?
        # probably other parameters
    ):
        self.country = pycountry.countries.get(name=country_name)

        # you can download country dataframe from GADM using
        # get_shape_data_by_country(country, ad_level)
        # if country "is pycountry"
        ...

    @staticmethod
    def retrieve_admin_area_names(
        country_gdf: GeoDataFrame, admin_level: int
    ) -> list[str]:
        """
        Given a country geodataframe and the administrative level granularity,
        retrieve the names of administrative areas.

        This function is mainly going to be used in the front end for users to select
        an administrative area from a drop-down list.

        Let op: admin_level > 0. Handle
        """
        ...

    def get_boundaries(self) -> Polygon | MultiPolygon:
        # boundaries of the administrative area
        ...

    def get_iso3_country_code(self) -> str:

        # this is how you access it if country is pycountry.countries.get(name=country_name)
        return self.country.alpha_3.lower()
