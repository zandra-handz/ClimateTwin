import geopandas as gpd 
import os
from django.conf import settings

class DatasetsLoader:
    @classmethod
    def load_countries_data(cls):
        countries_file_path = os.path.join(settings.STATIC_ROOT, 'climatevisitor', 'shapefiles', 'countries_indexed_on_SOV_A3.shp')
        dataset = gpd.read_file(countries_file_path)
        if dataset.crs is None:
            dataset.set_crs(epsg=4326, inplace=True)

        return dataset

    @classmethod
    def load_cities_data(cls):
        cities_file_path = os.path.join(settings.STATIC_ROOT, 'climatevisitor', 'shapefiles', 'world_cities_indexed_on_SOV_A3.shp')
        dataset = gpd.read_file(cities_file_path)
        if dataset.crs is None:
            dataset.set_crs(epsg=4326, inplace=True)

        return dataset
