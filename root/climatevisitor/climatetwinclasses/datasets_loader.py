from django.core.cache import cache
from django.conf import settings
  
import geopandas as gpd 
import os

class DatasetsLoader:
    @classmethod
    def load_countries_data(cls):
        countries_gdf = cache.get('countries_gdf')
        if countries_gdf is None:
            countries_file_path = os.path.join(settings.STATIC_ROOT, 'climatevisitor', 'geo_parquet', 'countries_indexed_on_SOV_A3_simplified.parquet')
            dataset = gpd.read_parquet(countries_file_path)

            # I preprocessed parquet file, so commenting out below in this case
            # if dataset.crs is None:
            #     dataset.set_crs(epsg=4326, inplace=True)

            countries_gdf = dataset
            cache.set('countries_gdf', countries_gdf, timeout=86400)  # Cache for 1 day

        return countries_gdf

    @classmethod
    def load_cities_data(cls):
        cities_gdf = cache.get('cities_gdf')
        if cities_gdf is None:
            cities_file_path = os.path.join(settings.STATIC_ROOT, 'climatevisitor', 'geo_parquet', 'world_cities_indexed_on_SOV_A3.parquet')
            dataset = gpd.read_parquet(cities_file_path)

            # I preprocessed parquet file, so commenting out below in this case
            # if dataset.crs is None:
            #     dataset.set_crs(epsg=4326, inplace=True)

            cities_gdf = dataset
            cache.set('cities_gdf', cities_gdf, timeout=86400)  # Cache for 1 day

        return cities_gdf
