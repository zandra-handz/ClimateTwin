
from django.conf import settings
from shapely.geometry import Point
import geopandas as gpd
import numpy as np 
import requests

# Added for websocket
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# Actual keys are in settings.py
google_api_key = settings.GOOGLE_MAPS_API_KEY
open_map_api_key = settings.OPEN_MAP_API_KEY


class ExperienceLocation:

    def __init__(self, lat, lon, units='imperial', experience_mode_for_existing_location=None, prev_lat=None, prev_lon=None, prev_address=None, relational=True):

        self.api_key = open_map_api_key
        self.google_api_key = google_api_key
        self.prev_lat = prev_lat
        self.prev_lon = prev_lon
        self.lat = lat
        self.lon = lon
        self.climate = None
        # self.units = units
        self.weather_info = None 
        self.address = None
        self.location = None 

        self.prev_lat = prev_lat
        self.prev_lon = prev_lon
        self.prev_address = prev_address
        self.prev_weather_info = None
        self.prev_location = None
        self.relational = relational
        self.experience_mode_for_existing_location = experience_mode_for_existing_location


        self.weather_info = self.get_weather(self.lat, self.lon)

        if not self.weather_info:
            raise ValueError(f"Could not get weather details.")

        
        if self.relational:
            self.prev_weather_info = self.get_weather(self.prev_lat, self.prev_lon)


            if not self.prev_weather_info:
                raise ValueError(f"Could not get previous weather details.")
            
            # this is get_home_climate from Twin Finder
            prev_address = self.prev_address
            prev_weather_info = self.prev_weather_info
            self.prev_location = {prev_address: prev_weather_info}

        
        if self.experience_mode_for_existing_location:
            if isinstance(self.experience_mode_for_existing_location, dict):
                name = next(iter(self.experience_mode_for_existing_location))
                self.address = str(name)

                self.location = {self.address: self.weather_info}
            
                try: 
                    self.location.update(self.experience_mode_for_existing_location[self.address])

                except (ValueError): 
                    raise ValueError("The data passed in is in the wrong format (must be a dictionary inside of a single key value dictionary)")
            else: 
                raise TypeError("Experience mode data must be a dictionary")
        else: 
            raise TypeError("Must pass in data here for right now")
            
        
            






    def __str__(self):
        return f"Experience Location for {self.lat}, {self.lon}"


    def get_weather(self, lat, lon):
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "units": self.units,
            "appid": self.api_key,
        }

        response = requests.get(base_url, params=params)
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
