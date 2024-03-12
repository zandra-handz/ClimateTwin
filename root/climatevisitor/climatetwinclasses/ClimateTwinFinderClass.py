from climatevisitor.tasks.tasks import send_coordinate_update_to_celery, send_location_update_to_celery
from celery import shared_task, current_app
from django.conf import settings
import geopandas as gpd
import numpy as np 
import requests

# Added for websocket
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# Actual keys are in settings.py
google_api_key = settings.GOOGLE_MAPS_API_KEY
open_map_api_key = settings.OPEN_MAP_API_KEY


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
    

        
    """


    def __init__(self, user_id_for_celery, address, units='imperial'):

        self.api_key = open_map_api_key
        self.google_api_key = google_api_key
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

        self.user_id_for_celery = user_id_for_celery

        coordinates = self.validate_address(address)

        if not coordinates:
            raise ValueError(f"Invalid address: {address}")
        else:
            self.origin_lat = coordinates[0]
            self.origin_lon = coordinates[1]
            print(self.origin_lat)

            print("Address validated!")

            self.weather_info = self.get_weather(self.origin_lat, self.origin_lon)

            if not self.weather_info:
                raise ValueError(f"Could not get weather details.")

        self.get_home_climate()

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
        self.print_home_climate_profile_concise()
        self.print_climate_twin_profile_concise()
        self.print_algorithm_data()


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
        print(f"OpenWeatherMap calls: {self.key_count}")
        print(f"GoogleMap calls: {self.google_key_count}")
        print(f"High variances: {self.high_variance_count}")



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
            print(f"Error: Unable to retrieve weather data for {lat}, {lon}")
            return None


    def get_home_climate(self):
        weather_info = self.weather_info
        address = self.address
        self.home_climate = {address: weather_info}


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
            print(f"COORDINATES: {location}")
            return location['lat'], location['lng']
        else:
            print(f"Error: Unable to retrieve coordinates for {address}")
            return None




    def generate_random_points_within_bounds(self, bounds, num_points):
        minx, miny, maxx, maxy = bounds
        x = np.random.uniform(minx, maxx, num_points)
        y = np.random.uniform(miny, maxy, num_points)
        points = gpd.GeoDataFrame(geometry=gpd.points_from_xy(x, y))
        return points



    def generate_random_coords_in_a_country_list(self):
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

        # Exclude ocean areas from the dataset
        land_only = world[world['geometry'].is_empty == False]

        # Simplify the geometry for efficiency
        land_only['simplified_geometry'] = land_only['geometry'].simplify(tolerance=0.01)

        # Create a spatial index
        spatial_index = land_only.sindex

        # Generate random points within one randomly selected country
        num_points = 14
        recalculations = 0

        while True:
            recalculations += 1
            # Randomly select one country
            random_country_idx = np.random.choice(land_only.index)
            random_country = land_only.loc[random_country_idx]

            # For algorithm viewing and animation debugging
            try:
                country_name = random_country['name']   
            except KeyError:
                country_name = 'Mystery Country'  

            # Use spatial index for efficient point-in-polygon check
            possible_matches_index = list(spatial_index.intersection(random_country.geometry.bounds))
            possible_matches = land_only.iloc[possible_matches_index]

            # Extract the simplified geometry from the first matching feature
            simplified_geometry = possible_matches.simplified_geometry.iloc[0]

            # Generate random points within the selected country
            points_within_country = self.generate_random_points_within_bounds(simplified_geometry.bounds, num_points)

            # Check if the generated points fall within land polygons
            if all(land_only.geometry.contains(point).any() for point in points_within_country.geometry):
                break

        print(f"Country picker recalculations: {recalculations}")
        return country_name, points_within_country



    # Old approach that has been sidelined
    def generate_random_points_within_country_old(self):
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

        # Simplify the geometry for efficiency
        world['simplified_geometry'] = world['geometry'].simplify(tolerance=0.01)

        # Create a spatial index
        spatial_index = world.sindex

        # Generate 10 random points within one randomly selected country
        num_points = 14

        # Randomly select one country
        random_country_idx = np.random.choice(world.index)
        random_country = world.loc[random_country_idx]

        # Use spatial index for efficient point-in-polygon check
        possible_matches_index = list(spatial_index.intersection(random_country.geometry.bounds))
        possible_matches = world.iloc[possible_matches_index]

        # Extract the simplified geometry from the first matching feature
        simplified_geometry = possible_matches.simplified_geometry.iloc[0]

        # Generate random points within the selected country
        points_within_country = self.generate_random_points_within_bounds(simplified_geometry.bounds, num_points)

        return points_within_country


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
        num_places = 5
        high_variance = 0
        celery_fail_count = 0

        while num_places > len(self.similar_places['name']):
            country_name, random_coords = self.generate_random_coords_in_a_country_list()

            for idx, point in random_coords.iterrows():
                latitude, longitude = point.geometry.y, point.geometry.x

                weather = self.get_weather(latitude, longitude)

                if weather:
                    temperature = weather['temperature']
                    temperature = round(int(temperature))
                    temperature_difference = abs(weather['temperature'] - self.weather_info['temperature'])
                    print(temperature_difference)
                    

                    if celery_fail_count < 3:
                        try:
                            # Send coordinates update via WebSocket
                            #self.send_coordinate_update(latitude, longitude)
                            send_coordinate_update_to_celery(user_id=self.user_id_for_celery, country_name=country_name, temperature=temperature, latitude=latitude, longitude=longitude)
                        except Exception as e:
                            print(f"Error sending to Celery task: {e}")
                            celery_fail_count += 1
                            continue


                    if temperature_difference < 3:
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

                        # Check if we have found the desired number of places
                        if num_places <= len(self.similar_places['name']):
                            break

                    else:
                        if temperature_difference > 14:
                            high_variance += 1
                            self.high_variance_count += 1
                            print(f"High variance: {high_variance}")
                            if high_variance > 2:
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

        print(f"Found {len(self.similar_places['name'])}")



    def humidity_comparer(self):
        print(self.similar_places)
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
        print(f"CLOSEST HUMIDITY = {closest_humidity}")
        places_semifinalists = self.similar_places
        climate_twin = {}

        for name, temp, desc, wind_speed, wind_direction, humidity, pressure, cloudiness, sunrise_timestamp, sunset_timestamp, latitude, longitude in zip(
                places_semifinalists['name'], places_semifinalists['temperature'], places_semifinalists['description'],
                places_semifinalists['wind_speed'], places_semifinalists['wind_direction'], places_semifinalists['humidity'],
                places_semifinalists['pressure'], places_semifinalists['cloudiness'], places_semifinalists['sunrise_timestamp'],
                places_semifinalists['sunset_timestamp'], places_semifinalists['latitude'], places_semifinalists['longitude']):

            if humidity == closest_humidity:
                results = self.reverse_geocode(latitude, longitude)
                print(f"GEOCODE RESULTS: {results}")
                country = results['country']
                if country is None: # or not country.strip() or "None":
                    print("FIND CLIMATE TWIN RETURNED FALSE ON COUNTRY CHECK")
                    return False
                location_name = results['location_name']
                location_name = results['location_name']
                location_name = results['location_name']
                location_name = results['location_name']
                city = results['city']


                print(f"location name: {location_name}")

                print(f"country: {country}")

                if " " in location_name:
                    code, address = location_name.split(" ", 1)
                    complete_address = f"{address}"

                else:
                    if country:
                        complete_address = f"Uncharted location in {country}"
                    else:
                        print("FIND CLIMATE TWIN RETURNED FALSE")
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
                send_location_update_to_celery(user_id=self.user_id_for_celery, temperature=temperature, name=address_str, latitude=latitude, longitude=longitude)
                
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
            print(header)

            num_entries = len(values[0])
            for i in range(num_entries):
                row_values = [str(values[j][i]) for j in range(len(keys))]
                row = "\t".join(row_values)
                print(row)

