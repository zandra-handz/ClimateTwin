from climatevisitor.tasks.tasks import send_coordinate_update_to_celery, send_location_update_to_celery
from celery import shared_task, current_app
from django.conf import settings
from django.core.cache import cache
from shapely.geometry import Point
from shapely.geometry import MultiPolygon, Polygon
import geopandas as gpd
import numpy as np 
import requests 
import os

# Added for websocket
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

 





# Actual keys are in settings.py
google_api_key = settings.GOOGLE_MAPS_API_KEY
open_map_api_key = settings.OPEN_MAP_API_KEY



import logging

logger = logging.getLogger(__name__)


class ClimateTwinFinder:

    """

    This class performs the search via instance initialization.

    The rundown:

    - Loads Open Weather Map and Google Map keys
    - Loads address
    - Loads units to measure distance in
    - Loads similar_places with empty dict with additioanl top level key 'name' added
    - Checks if address is valid using Google Maps call https://maps.googleapis.com/maps/api/geocode/json and assigns results to 'coordinates'
    - If not coordinates, raises invalid address ValueError
    - Loads coordinates into origin_lat and origin_lon; if not coordinates, raises invalid address ValueError
    - Loads weather_info by running get_weather function which uses Open Weather Map call https://api.openweathermap.org/data/2.5/weather; if not weather_info, raises ValueError
    - Updates home_climate by running get_home_climate(), which combines address and weather_info 
    - Sets 'successful' variable for twin climate finder function to False
    - Inside 'successful' variable While loop:
        - Runs completion_checker_similar_places() until five candidate places are found
        - Sets 'successful' variable to managing_function_to_find_climate_twin() result
        - managing_function_to_find_climate_location() identifies location(s) with closest humidity and checks for sufficient data
          (specifically, country value; if no country value, this suggests the location is not a populated area and the function returns False)
        - If successful, climate_twin was loaded with data and the While loop terminates
        - If not successful, similar_places gets reset and the While loop tries again.

    
    Areas of possible improvement:

    - Some functions are likely unnecessary and weird middlemen left over from previous versions, that can be removed as long as stil readable
    - Search algorithm completion time varies more widely than I like.
    - Small countries are given as many search allowances as larger countries, not ideal

        
    """


    def __init__(self, user_id_for_celery, address, units='imperial'):

        self.api_key = open_map_api_key
        self.google_api_key = google_api_key
        self.preset_divider_for_point_gen_deviation = 6 #4
        self.preset_matches_per_country_allowed = 2 # added 3/22/25, intended purpose: more varied results
        self.preset_num_final_candidates_required = 6 #4
        self.preset_temp_diff_is_high_variance = 18 #12
        self.preset_num_high_variances_allowed = 3 #2
        self.preset_points_generated_in_each_country = 30
        self.origin_lat = 0
        self.origin_lon = 0
        self.google_key_count = 0
        self.key_count = 0
        self.high_variance_count = 0
        self.address = address
        self.home_climate = None
        self.units = units
        self.weather_info = None 
        self.similar_places = self.configure_similar_places_dict()
        self.search_cycle = 0
        self.climate_twin = None
        self.countries_searched = 0
        self.countries_list = []
        self.dataset_len_cities_in_country = 0
        self.cities_matched = 0
        self.cities_list = []
        self.points_generated = 0
        self.points_generated_on_land = 0
        self.home_temperature = 0
        self.climate_twin_address = None
        self.climate_twin_temperature = 0
        self.climate_twin_lat = 0
        self.climate_twin_lon = 0
        self.dataset_for_countries = None
        self.dataset_for_cities = None
 


        self.user_id_for_celery = user_id_for_celery

        coordinates = self.validate_address(address)

        if not coordinates:
            raise ValueError(f"Invalid address: {address}")
        else:
            self.origin_lat = coordinates[0]
            self.origin_lon = coordinates[1]
            # print(self.origin_lat)

            # print("Address validated!")

            self.weather_info = self.get_weather(self.origin_lat, self.origin_lon)

            if not self.weather_info:
                raise ValueError(f"Could not get weather details.")

        self.get_home_climate()

        # Reads in dataset once at the start of the algorithm
        # self.dataset_for_countries = self.read_in_countries_dataset()
        # self.dataset_for_cities = self.read_in_cities_dataset()

        self.dataset_for_countries = cache.get('countries_gdf')
        if self.dataset_for_countries is None:
            logger.info('No countries data in datasets cache. Loading countries...')
            self.dataset_for_countries = self.read_in_countries_dataset()
            cache.set('countries_gdf', self.dataset_for_countries, timeout=86400) 

        self.dataset_for_cities = cache.get('cities_gdf')
        if self.dataset_for_cities is None:
            logger.info('No cities data in datasets cache. Loading cities...')
            self.dataset_for_cities = self.read_in_cities_dataset()
            cache.set('cities_gdf', self.dataset_for_cities, timeout=86400) 

        


        successful = False

        # May handle differently in future
        while not successful:

            # Finds five candidate places
            five_locations_found = self.completion_checker_similar_places()

            if five_locations_found:
            # Selects one or more with closest humidity, returns False if no value for country
                successful = self.managing_function_to_find_climate_twin()

            self.configure_similar_places_dict()


        # Debug statements
        # self.print_home_climate_profile_concise()
        # self.print_climate_twin_profile_concise()
        self.print_algorithm_data()
        self.log_algorithm_data()


    def __str__(self):
        return f"Weather twins for {self.address}"


    # Debug function
    def print_climate_twin_profile_concise(self):
        for name, data in self.climate_twin.items():

            print(f"Climate twin: {name}")
            print("~~~~~~")
            print(f"Temperature: {data['temperature']} °F")
            print(f"Description: {data['description']}")
            print(f"Humidity: {data['humidity']}%")
            print(f"Cloudiness: {data['cloudiness']}%")
            print("\n")


    # Debug function
    def print_home_climate_profile_concise(self):
        for name, data in self.home_climate.items():

            print(f"Home: {name}")
            print("~~~~~~")
            print(f"Temperature: {data['temperature']} °F")
            print(f"Description: {data['description']}")
            print(f"Humidity: {data['humidity']}%")
            print(f"Cloudiness: {data['cloudiness']}%")
            print("\n")


    # Debug function
    def print_algorithm_data(self):
        print(f"Home address: {self.address}")
        # The below works, but easier to make a new property so I did
        # print(f"Home temp: {self.home_climate[self.address]['temperature']}")
        print(f"Home temperatire: {self.home_temperature}")
        print(f"Twin address: {self.climate_twin_address}")
        print(f"Twin temperature: {self.climate_twin_temperature}") 
        print(f"OpenWeatherMap calls: {self.key_count}")
        print(f"GoogleMap calls: {self.google_key_count}")
        print(f"High variances: {self.high_variance_count}")
        print(f"Countries searched: {self.countries_searched}")
        print(f"Countries list: {self.countries_list}")
        print(f"Cities matched: {self.cities_matched}")
        print(f"Cities list: {self.cities_list}")
        print(f"Points searched: {self.points_generated_on_land}")
        print(f"Total points generated: {self.points_generated}")
        print(f"PRESET: Matched locations per country allowed: {self.preset_matches_per_country_allowed}")
        print(f"PRESET: Random points to generate in each country: {self.preset_points_generated_in_each_country}")
        print(f"PRESET: Temp dif is high variance: {self.preset_temp_diff_is_high_variance}")
        print(f"PRESET: Number of high variances allowed: {self.preset_num_high_variances_allowed}")
        print(f"PRESET: Divider for point generation deviation: {self.preset_divider_for_point_gen_deviation}")
        print(f"PRESET: Number of final location candidates required: {self.preset_num_final_candidates_required}")


    # Debug function, may turn this data into model instances and save in DB later
    def log_algorithm_data(self):
        logger.info(f"Home address: {self.address}")
        # The below works, but easier to make a new property so I did
        # logger.info(f"Home temp: {self.home_climate[self.address]['temperature']}")
        logger.info(f"Home temperatire: {self.home_temperature}")
        logger.info(f"Twin address: {self.climate_twin_address}")
        logger.info(f"Twin temperature: {self.climate_twin_temperature}")

        logger.info(f"OpenWeatherMap calls: {self.key_count}")
        logger.info(f"GoogleMap calls: {self.google_key_count}")
        logger.info(f"High variances: {self.high_variance_count}")
        logger.info(f"Countries searched: {self.countries_searched}")
        logger.info(f"Countries list: {self.countries_list}")
        logger.info(f"Cities matched: {self.cities_matched}")
        logger.info(f"Cities list: {self.cities_list}")
        logger.info(f"Points searched: {self.points_generated_on_land}")
        logger.info(f"Total points generated: {self.points_generated}")
        logger.info(f"PRESET: Matched locations per country allowed: {self.preset_matches_per_country_allowed}")
        logger.info(f"PRESET: Random points to generate in each country: {self.preset_points_generated_in_each_country}")
        logger.info(f"PRESET: temp dif is high variance: {self.preset_temp_diff_is_high_variance}")
        logger.info(f"PRESET: Number of high variances allowed: {self.preset_num_high_variances_allowed}")
        logger.info(f"PRESET: Divider for point generation deviation: {self.preset_divider_for_point_gen_deviation}")
        logger.info(f"PRESET: Number of final location candidates required: {self.preset_num_final_candidates_required}")



    def validate_address(self, address):
        return self.get_coordinates(address)


    def configure_similar_places_dict(self):
        self.similar_places = {}
        self.similar_places['name'] = []

        return self.similar_places


    def get_weather(self, lat, lon):
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "units": self.units,
            "appid": self.api_key,
        }

        response = requests.get(base_url, params=params)
        self.key_count += 1
        data = response.json()

        if response.status_code == 200:
            temperature = data["main"]["temp"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]
            wind_direction = data["wind"]["deg"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            cloudiness = data["clouds"]["all"]
            sunrise_timestamp = data["sys"]["sunrise"]
            sunset_timestamp = data["sys"]["sunset"]

            info = {
                'temperature': temperature,
                'description': description,
                'wind_speed': wind_speed,
                'wind_direction': wind_direction,
                'humidity': humidity,
                'pressure': pressure,
                'cloudiness': cloudiness,
                'sunrise_timestamp': sunrise_timestamp,
                'sunset_timestamp': sunset_timestamp,
                'latitude': lat,
                'longitude': lon,
            }

            return info
        else:
            # Debug statement
            # print(f"Error: Unable to retrieve weather data for {lat}, {lon}")
            return None


    def get_home_climate(self):
        weather_info = self.weather_info
        address = self.address
        self.home_climate = {address: weather_info}

        # Added for easier record keeping
        self.home_temperature = weather_info['temperature']


    def get_coordinates(self, address):
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.google_api_key
        }

        response = requests.get(base_url, params=params)
        self.google_key_count += 1
        data = response.json()

        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            # print(f"COORDINATES: {location}")
            return location['lat'], location['lng']
        else:
            # print(f"Error: Unable to retrieve coordinates for {address}")
            return None



    # Alternative to points_with_polygon; not in use
    # def generate_random_points_within_bounds(self, bounds, num_points):
    #     minx, miny, maxx, maxy = bounds
    #     x = np.random.uniform(minx, maxx, num_points)
    #     y = np.random.uniform(miny, maxy, num_points)
    #     points = gpd.GeoDataFrame(geometry=gpd.points_from_xy(x, y))
    #     return points



    def generate_random_points_within_polygon(self, polygon, num_points, city_location=None):

        # smaller distance from center: 6
        std_dev_divider = self.preset_divider_for_point_gen_deviation

        if not isinstance(polygon, (Polygon, MultiPolygon)):
            return gpd.GeoDataFrame(geometry=[]) 

        # If a city location is provided, use it as the starting point; otherwise, use the centroid
        
        
        
        if city_location is not None: 
            # centroid = polygon.centroid
            # centroid_x, centroid_y = centroid.x, centroid.y

            centroid_x, centroid_y = city_location
        else:
            centroid = polygon.centroid
            centroid_x, centroid_y = centroid.x, centroid.y
        
        minx, miny, maxx, maxy = polygon.bounds
        std_dev_x = (maxx - minx) / std_dev_divider
        std_dev_y = (maxy - miny) / std_dev_divider

        x = np.random.normal(centroid_x, std_dev_x, num_points)
        y = np.random.normal(centroid_y, std_dev_y, num_points)

        points = [Point(px, py) for px, py in zip(x, y) if polygon.contains(Point(px, py))]
        points_gdf = gpd.GeoDataFrame(geometry=points)



        return points_gdf
 
    def read_in_countries_dataset(self): 
        countries_file_path = os.path.join(settings.STATIC_ROOT, 'climatevisitor', 'geo_parquet', 'countries_indexed_on_SOV_A3_land_only_minimal_columns.parquet')
        
        dataset = gpd.read_parquet(countries_file_path)

        return dataset



    def read_in_cities_dataset(self):
       # return gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))

        cities_file_path = os.path.join(settings.STATIC_ROOT, 'climatevisitor', 'geo_parquet', 'world_cities_indexed_on_SOV_A3.parquet')
        
        dataset = gpd.read_parquet(cities_file_path)

        # I preprocessed parquet file, so commenting out below in this case
        if dataset.crs is None:
            dataset.set_crs(epsg=4326, inplace=True)

        return dataset

        #self.dataset_for_cities = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))

        #cities_file_path = os.path.join(settings.STATIC_ROOT, 'climatevisitor','shapefiles', 'ne_110m_populated_places.shp')
        
        #self.dataset_for_cities = gpd.read_file(cities_file_path)
       # logger.info(self.dataset_for_cities.head())


        # try:
        #     self.dataset_for_cities = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))
        #     logger.info('Cities data set read in successfully')
        #     print(self.dataset_for_cities.head()) 
        #     logger.info(self.dataset_for_cities.head())
        # except Exception as e:
        #     logger.error('Could not read cities data set in, error:', e)







    def generate_random_coords_in_a_country_list(self):
        world = self.dataset_for_countries
        cities = self.dataset_for_cities

        # MOVED TO PREPROCESSING OF FILE
        # Exclude ocean areas from the dataset  
        # land_only = world[world['geometry'].is_empty == False]
        # land_only['simplified_geometry'] = land_only['geometry'].simplify(tolerance=0.01)
 
        num_points = self.preset_points_generated_in_each_country
        logger.info(f"self.points_generated_in_each_country: {num_points}")
        
        recalculations = 0
        len_cities = 0
        points_within_country = gpd.GeoDataFrame(geometry=[])

        while True:
            recalculations += 1
 
            random_country_idx = np.random.choice(world.index)
            random_country = world.loc[random_country_idx]

            # For algorithm viewing and animation debugging
            # This country name is sent to front end via a websocket, and used to log the country as well
            try:
                country_name = random_country['SOVEREIGNT']   # SOVEREIGNT to match dataset
            except KeyError:
                country_name = 'Mystery Country'  
 
                    
            if not cities.empty:

                if cities.crs != world.crs:
                    cities = cities.to_crs(world.crs)
 
                # Finds cities with matching SOV_A3 to country
                # Both datasets are parquet files (as of 3/22/2025) indexed on SOV_A3
                cities_in_country = cities[cities.index == random_country_idx] 

                if not cities_in_country.empty: 

                    self.cities_matched += 1 

                    len_cities = len(cities_in_country)
                    self.dataset_len_cities_in_country = len_cities

                    # Alternative to sample, slightly faster but doesn't have additional functionalities like weighted sampling
                    random_index = np.random.randint(0, len_cities)
                    city_row = cities_in_country.iloc[random_index]

                    # Using numpy above instead
                    # city_row = cities_in_country.sample(1)
                   

                    self.cities_list.append(city_row.city_ascii)
                    
                    try:
                        city_location = (city_row.geometry.x.values[0], city_row.geometry.y.values[0])
                    except IndexError:  
                        city_location = None 
                else:
                    city_location = None   


            points_within_country = self.generate_random_points_within_polygon(
                random_country['geometry'], num_points, city_location=city_location)

            if points_within_country is None or points_within_country.empty:
                logger.warning("Warning: No points generated within country")
                continue

            if len(points_within_country) > 0:  # Explicitly check if it's non-empty
                self.points_generated += len(points_within_country)

                points_within_country = points_within_country[points_within_country.geometry.apply(
                    lambda point: world.geometry.contains(point).any())]
                if len(points_within_country) > 0:
                    self.points_generated_on_land += len(points_within_country)
 
                    self.countries_searched += 1
                    self.countries_list.append((country_name, f"cities in dataset: {len_cities}"))
                    self.dataset_len_cities_in_country = 0 # Reset

                    break
          

            # Check if the generated points fall within land polygons
            # if all(land_only.geometry.contains(point).any() for point in points_within_country.geometry):
            #     break

        # print(f"Country picker recalculations: {recalculations}")
        return country_name, points_within_country



    # # Old approach that has been sidelined
    # def generate_random_points_within_country_old(self):
    #     world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    #     # Simplify the geometry for efficiency
    #     world['simplified_geometry'] = world['geometry'].simplify(tolerance=0.01)

    #     # Create a spatial index
    #     spatial_index = world.sindex

    #     # Generate 10 random points within one randomly selected country
    #     num_points = 14

    #     # Randomly select one country
    #     random_country_idx = np.random.choice(world.index)
    #     random_country = world.loc[random_country_idx]

    #     # Use spatial index for efficient point-in-polygon check
    #     possible_matches_index = list(spatial_index.intersection(random_country.geometry.bounds))
    #     possible_matches = world.iloc[possible_matches_index]

    #     # Extract the simplified geometry from the first matching feature
    #     simplified_geometry = possible_matches.simplified_geometry.iloc[0]

    #     # Generate random points within the selected country
    #     points_within_country = self.generate_random_points_within_bounds(simplified_geometry.bounds, num_points)

    #     return points_within_country


    # Finds twin location or returns None
    def completion_checker_similar_places(self):

        result = self.search_random_coords_in_a_country()

        if result:
            return True

        else:
            return

    # Added for websocket


    def search_random_coords_in_a_country(self):
        base_url = "https://api.openweathermap.org/data/2.5/find"
        num_places = self.preset_num_final_candidates_required
        high_variance = 0
        high_variance_trigger = self.preset_temp_diff_is_high_variance # degree difference that will add to high variance count
        high_variance_count_limit = self.preset_num_high_variances_allowed # once count exceeds, algo will ditch search in current country and go to new country
        celery_fail_count = 0

        found_count = self.preset_matches_per_country_allowed

        while num_places > len(self.similar_places['name']):
            country_name, random_coords = self.generate_random_coords_in_a_country_list()

            for idx, point in random_coords.iterrows():
                latitude, longitude = point.geometry.y, point.geometry.x

                weather = self.get_weather(latitude, longitude)

                if weather:
                    temperature = weather['temperature']
                    temperature = round(int(temperature))
                    temperature_difference = abs(weather['temperature'] - self.weather_info['temperature'])

                    # For algo websocket only
                    temperature_difference_rounded = round(int(temperature_difference))
                    
                    # print(temperature_difference)
                    

                    if celery_fail_count < 3:
                        try:
                            # Send coordinates update via WebSocket
                            #self.send_coordinate_update(latitude, longitude)
                            send_coordinate_update_to_celery(user_id=self.user_id_for_celery, country_name=country_name, temperature=temperature, temp_difference=temperature_difference_rounded, latitude=latitude, longitude=longitude)
                        except Exception as e:
                            # print(f"Error sending to Celery task: {e}")
                            celery_fail_count += 1
                            continue


                    if temperature_difference < 2:
                        # Process and add the new entry to self.similar_places
                        new_entry = {
                            'name': [f'climate twin candidate'],
                            'temperature': weather['temperature'],
                            'description': weather['description'],
                            'wind_speed': weather['wind_speed'],
                            'wind_direction': weather['wind_direction'],
                            'humidity': weather['humidity'],
                            'pressure': weather['pressure'],
                            'cloudiness': weather['cloudiness'],
                            'sunrise_timestamp': weather['sunrise_timestamp'],
                            'sunset_timestamp': weather['sunset_timestamp'],
                            'latitude': weather['latitude'],
                            'longitude': weather['longitude']
                        }
                        self.process_new_entry(new_entry)

                        found_count += 1

                        # Check if we have found the desired number of places
                        if num_places <= len(self.similar_places['name']):
                            break

                    else:
                        # Only two finds allowed per country
                        if found_count > 1:
                            self.preset_matches_per_country_allowed = 0 # Reset before breaking
                            break
                        if temperature_difference > high_variance_trigger:
                            high_variance += 1
                            self.high_variance_count += 1
                            # print(f"High variance: {high_variance}")
                            if high_variance > high_variance_count_limit:
                                # Reset high_variance and break to get new coordinates
                                high_variance = 0
                                break

                else:
                    print("missing weather data")

        return True



    def process_new_entry(self, new_entry):

        # Process and add the new entry to self.similar_places
        if 'similar_places' not in self.__dict__:
            self.similar_places = {
                'name': [],
                'temperature': [],
                'description': [],
                'wind_speed': [],
                'wind_direction': [],
                'humidity': [],
                'pressure': [],
                'cloudiness': [],
                'sunrise_timestamp': [],
                'sunset_timestamp': [],
                'latitude': [],
                'longitude': []
            }

        for key, value in new_entry.items():
            if key not in self.similar_places:
                self.similar_places[key] = []
            self.similar_places[key].append(value)

        # print(f"Found {len(self.similar_places['name'])}")



    def humidity_comparer(self):
        # print(self.similar_places)
        difference = 100
        closest = 0
        for value in self.similar_places['humidity']:
            new_difference = value - self.weather_info['humidity']
            new_difference = abs(new_difference)
            if new_difference < difference:
                difference = new_difference
                closest = value
        return closest





    def reverse_geocode(self, latitude, longitude):
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{latitude},{longitude}",
            "key": self.google_api_key,
        }

        response = requests.get(base_url, params=params)
        self.google_key_count += 1
        data = response.json()

        if response.status_code == 200:
            # Check if the response contains any results
            if data["status"] == "OK" and len(data.get("results", [])) > 0:
                # Extract the formatted address (location name) from the first result
                location_name = data["results"][0]["formatted_address"]

                # Extract the city name
                city = next((component["long_name"] for result in data["results"] for component in result.get("address_components", []) if "locality" in component["types"]), None)

                # Extract the country name from the address components
                country = next((component["long_name"] for result in data["results"] for component in result.get("address_components", []) if "country" in component["types"]), None)

                return {
                    "location_name": location_name,
                    "city": city,
                    "country": country
                }
        else:
            print(f"Error: {data['status']} - {data.get('error_message', 'Unknown error')}")

        return None




    def managing_function_to_find_climate_twin(self):
        closest_humidity = self.humidity_comparer()
        # print(f"CLOSEST HUMIDITY = {closest_humidity}")
        places_semifinalists = self.similar_places
        climate_twin = {}

        for name, temp, desc, wind_speed, wind_direction, humidity, pressure, cloudiness, sunrise_timestamp, sunset_timestamp, latitude, longitude in zip(
                places_semifinalists['name'], places_semifinalists['temperature'], places_semifinalists['description'],
                places_semifinalists['wind_speed'], places_semifinalists['wind_direction'], places_semifinalists['humidity'],
                places_semifinalists['pressure'], places_semifinalists['cloudiness'], places_semifinalists['sunrise_timestamp'],
                places_semifinalists['sunset_timestamp'], places_semifinalists['latitude'], places_semifinalists['longitude']):

            if humidity == closest_humidity:
                results = self.reverse_geocode(latitude, longitude)
                # print(f"GEOCODE RESULTS: {results}")
                country = results['country']
                if country is None: # or not country.strip() or "None":
                    # print("FIND CLIMATE TWIN RETURNED FALSE ON COUNTRY CHECK")
                    return False
                location_name = results['location_name']
                location_name = results['location_name']
                location_name = results['location_name']
                location_name = results['location_name']
                city = results['city']


                # print(f"location name: {location_name}")

                # print(f"country: {country}")

                if " " in location_name:
                    code, address = location_name.split(" ", 1)
                    complete_address = f"{address}"

                else:
                    if country:
                        complete_address = f"an uncharted location in {country}"
                    else:
                        # print("FIND CLIMATE TWIN RETURNED FALSE")
                        return False

                address_str = complete_address

                climate_twin[address_str] = {
                    'temperature': temp,
                    'description': desc,
                    'wind_speed': wind_speed,
                    'wind_direction': wind_direction,
                    'humidity': humidity,
                    'pressure': pressure,
                    'cloudiness': cloudiness,
                    'sunrise_timestamp': sunrise_timestamp,
                    'sunset_timestamp': sunset_timestamp,
                    'latitude': latitude,
                    'longitude': longitude
                }

                #this return ensures only one location; comment out to allow for multiple
                self.climate_twin = climate_twin

                # Added for easier record keeping
                self.climate_twin_address = address_str
                self.climate_twin_temperature = temp
                self.climate_twin_lat = latitude
                self.climate_twin_lon = longitude

                # moved to parent algorithms_task to send AFTER this instance is saved and after it is then saved as current explore location
               # will ONLY be sending explore locations as location updates (except for 'is home' and potentially 'is in flight')
               # send_location_update_to_celery(user_id=self.user_id_for_celery, temperature=temp, name=address_str, latitude=latitude, longitude=longitude)

                return True


        self.climate_twin = climate_twin
        return True


    # Debug function
    def print_similar_places(self):
        places = self.similar_places
        if places:
            keys = list(places.keys())
            values = list(places.values())

            header = "\t".join(keys)
            # print(header)

            num_entries = len(values[0])
            for i in range(num_entries):
                row_values = [str(values[j][i]) for j in range(len(keys))]
                row = "\t".join(row_values)
                # print(row)

