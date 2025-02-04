from dataclasses import dataclass

from geopandas import GeoDataFrame
from numpy import ndarray
from pandas import DataFrame
from rasterio import DatasetReader
from shapely import MultiPolygon, Polygon


@dataclass
class Population:

    # remember to use "with" statement when getting resources

    data_source: str
    iso3_country_code: str
    admin_area_boundaries: Polygon | MultiPolygon
    population_resolution: int = 5

    def get_population_gdf(self) -> GeoDataFrame:
        """Integrates all the methods into one flow"""

        # define population_df according to the data_source given

        if self.data_source == "world_pop":
            population_df = self.get_population_worldpop()

        elif self.data_source == "facebook":
            population_df = self.get_population_facebook()

        # geojson or any other source can be added here in the future

        else:
            return  # handle error no valid data_source (consider Enum??)

        # check recency

        if not self.is_recent_data(population_df):
            # warn?
            ...

        # return grouped population

        return self.group_population(population_df, self.population_resolution)

        ...

    @staticmethod
    def group_population(population_df, population_resolution) -> GeoDataFrame: ...

    @staticmethod
    def is_recent_data(population_df: DataFrame) -> bool:

        # should this be implemented? Unsure how. What is a valid check? No longer than one year ago? Two? Five?
        ...

    ###### methods for dealing w facebook population start here #####
    def get_population_facebook(self) -> DataFrame:
        """
        - downloads data
        - processes data
        """

        downloaded_data = self.download_population_facebook(
            iso3_country_code=self.iso3_country_code,
            admin_area_boundaries=self.admin_area_boundaries,
        )

        processed_data = self.process_population_facebook(downloaded_data)

        return processed_data

    @staticmethod
    def download_population_facebook(
        iso3_country_code: str, admin_area_boundaries: Polygon | MultiPolygon
    ) -> DataFrame:
        # Download (somewhat raw) data from facebook
        ...

    @staticmethod
    def process_population_facebook(downloaded_data: DataFrame) -> DataFrame:
        # do the required processing
        ...

    ##### methods for dealing w worldpop population start here #####

    def get_population_worldpop(self) -> DataFrame:
        """
        - downloads data
        - processes data
        """

        downloaded_data = self.download_population_worldpop(
            iso3_country_code=self.iso3_country_code,
            admin_area_boundaries=self.admin_area_boundaries,
        )

        processed_data = self.process_population_worldpop(downloaded_data)

        return processed_data

    @staticmethod
    def download_population_worldpop(
        iso3_country_code: str, admin_area_boundaries: Polygon | MultiPolygon
    ) -> DataFrame:
        # download (somewhat raw) data from worldpop
        ...

    @staticmethod
    def process_population_worldpop(downloaded_data: DataFrame) -> DataFrame:

        # do the required processing (call raster_to_df)
        ...

    @staticmethod
    def raster_to_df(raster_fpath: str, mask_polygon: MultiPolygon):
        # I copy-pasted the signature from data_src, might need modification (can be Polygon?)
        ...

    @staticmethod
    def get_admarea_mask(
        vector_polygon: MultiPolygon, raster_layer: DatasetReader
    ) -> ndarray:

        # I copy-pasted the signature from data_src, might need modification (can be Polygon?)

        ...

    # if you want to add new data source (e.g. geojson):
    # create method get_population_gson(), and add a call to it in get_population_gdf
