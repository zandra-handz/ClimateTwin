from ..animations import update_animation
from ..consumer import ClimateTwinConsumer 
from asgiref.sync import async_to_sync
from celery import shared_task, current_app
from channels.layers import get_channel_layer
from climatevisitor.climatetwinclasses.ClimateTwinFinderClass import ClimateTwinFinder
from climatevisitor.climatetwinclasses.ClimateObjectClass import ClimateObject
from climatevisitor.climatetwinclasses.ClimateEncounterClass import ClimateEncounter
from climatevisitor.climatetwinclasses.OpenMapAPIClass import OpenMapAPI
from climatevisitor.models import ClimateTwinLocation
from climatevisitor import serializers
from time import sleep
from users.models import BadRainbowzUser, UserVisit
from users.serializers import BadRainbowzUserSerializer

import logging

logger = logging.getLogger(__name__)




@shared_task
def run_climate_twin_algorithms_task(user_id, user_address):
    sleep(2)
    print(f"run_climate_twin_algorithms_task initiated with args: {user_id}, {user_address}")

    try:
        user_instance = BadRainbowzUser.objects.get(pk=user_id)
    except BadRainbowzUser.DoesNotExist:
        print("Could not validate user.")
        return
    # Your task logic here, using the retrieved user object
    
    climate_places = ClimateTwinFinder(user_address)
    print("Twin Location found.")

    if climate_places.home_climate:
        address = list(climate_places.home_climate.keys())[0]
        home_data = climate_places.home_climate[address]
        home_data["name"] = address
        home_data["user"] = user_instance.id

        home_location_serializer = serializers.HomeLocationSerializer(data=home_data)
        if home_location_serializer.is_valid():
            home_location_instance = home_location_serializer.save()
        else:
            home_location_instance = None
            print("Error:", home_location_serializer.errors)

    if climate_places.climate_twin:
        home_weather_profile = ClimateObject(climate_places.home_climate)
        climate_twin_weather_profile = ClimateObject(climate_places.climate_twin)

        weather_encounter = ClimateEncounter(
            home_weather_profile.wind_direction,
            home_weather_profile.wind_speed,
            home_weather_profile.pressure,
            home_weather_profile.humidity,
            climate_twin_weather_profile.wind_direction,
            climate_twin_weather_profile.wind_speed,
            climate_twin_weather_profile.pressure,
            climate_twin_weather_profile.humidity
        )

        weather_messages = weather_encounter.combine_messages()

        climate_twin_location_instance = ClimateTwinLocation.create_from_dicts(
            user_instance, climate_places.climate_twin, weather_messages,
            home_location=home_location_instance
        )

        climate_twin_location_instance.save()

        osm_api = OpenMapAPI()
        osm_results = osm_api.find_ancient_ruins(climate_twin_weather_profile.latitude, climate_twin_weather_profile.longitude, radius=100000, num_results=15)
        nearby_ruins = osm_api.format_ruins_with_wind_compass_for_post(osm_results, climate_twin_weather_profile.wind_direction)

        for name, ruin in nearby_ruins.items():
            formatted_ruin = {
                "name": name,
                "user": user_instance.id,
                "direction_degree": ruin['direction_deg'],
                "direction": ruin.get('direction'),
                "miles_away": round(ruin['miles_away']),
                "location_id": ruin['id'],
                "latitude": ruin['latitude'],
                "longitude": ruin['longitude'],
                "tags": ruin["tags"],
                "wind_compass": ruin['wind_compass'],
                "wind_agreement_score": (round(ruin['wind_agreement_score'])),
                "wind_harmony": ruin['wind_harmony'],
                "street_view_image": ruin.get("street_view_image", ''),
                "origin_location": climate_twin_location_instance.id,
            }

            serializer = serializers.ClimateTwinDiscoveryLocationSerializer(data=formatted_ruin)
            if serializer.is_valid():
                discovery_location_instance = serializer.save(
                    user=user_instance  
                )
                print("Success: Discovery Location saved.")
            else:
                # Handle invalid data
                print("Error: Discovery Location could not be saved.")

        return "Success: Search completed!"
                
 
 


@shared_task(bind=True, max_retries=3)
def process_climate_twin_request(self, user_id, user_address):
    logger.info("Task to process climate twin request received.")
    
    print("Task to process climate twin request sent.")

    user_instance = BadRainbowzUser.objects.get(pk=user_id)

    try:
        run_climate_twin_algorithms_task(user_id, user_address)
    except Exception as exc:
        logger.error(f"Error processing climate twin request: {exc}. Retrying...")
        raise self.retry(exc=exc)
    
    logger.info("Task to process climate twin request completed.")
    return "Request sent for processing"
