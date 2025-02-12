from ..animations import update_animation
from ..consumer import ClimateTwinConsumer  

from climatevisitor.tasks.tasks import send_search_for_ruins_initiated, send_no_ruins_found, send_explore_locations_ready, send_clear_message
from asgiref.sync import async_to_sync
from celery import shared_task, current_app, current_task
from channels.layers import get_channel_layer
from climatevisitor.climatetwinclasses.ClimateTwinFinderClass import ClimateTwinFinder
from climatevisitor.climatetwinclasses.ClimateObjectClass import ClimateObject
from climatevisitor.climatetwinclasses.ClimateEncounterClass import ClimateEncounter
from climatevisitor.climatetwinclasses.OpenMapAPIClass import OpenMapAPI
from climatevisitor.models import ClimateTwinLocation, ClimateTwinExploreLocation, CurrentLocation
from climatevisitor import serializers
#from datetime import timezone
from django.core.cache import cache 
from django.utils import timezone 
import pytz
from time import sleep
from users.models import BadRainbowzUser, UserVisit
from users.serializers import BadRainbowzUserSerializer, UserVisitSerializer

import logging

logger = logging.getLogger(__name__)




@shared_task
def run_climate_twin_algorithms_task(user_id, user_address):
    sleep(0)
    print(f"run_climate_twin_algorithms_task initiated with args: {user_id}, {user_address}")

    try:
        user_instance = BadRainbowzUser.objects.get(pk=user_id)
    except BadRainbowzUser.DoesNotExist:
        print("Could not validate user.")
        return
    # Your task logic here, using the retrieved user object
    
    climate_places = ClimateTwinFinder(user_id_for_celery=user_id, address=user_address)
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

        
        user_visit_instance = UserVisit(user=user_instance, location_name=climate_twin_weather_profile.name,
                                        location_latitude=climate_twin_weather_profile.latitude,
                                         location_longitude=climate_twin_weather_profile.longitude)
        

        climate_twin_location_instance.save()
        user_visit_instance.save()

        send_search_for_ruins_initiated(user_id=user_instance.id)

        osm_api = OpenMapAPI()
        osm_results = osm_api.find_ancient_ruins(climate_twin_weather_profile.latitude, climate_twin_weather_profile.longitude, radius=100000, num_results=15)
        nearby_ruins = osm_api.format_ruins_with_wind_compass_for_post(osm_results, climate_twin_weather_profile.wind_direction)
        if not nearby_ruins:
            send_no_ruins_found(user_id=user_instance.id)

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
 
 
        try:
            explore_location_instance = ClimateTwinExploreLocation.objects.create(
                user=user_instance,
                twin_location=climate_twin_location_instance,
                created_on=timezone.now()  # Set creation time to current time
            )

            explore_location_instance.save()

        except Exception as e:
            print("An error occurred:", e)



        try:
            current_location = CurrentLocation.update_or_create_location(user=user_instance, twin_location=climate_twin_location_instance)
            
             # Schedule the expiration task after updating or creating the current location
            schedule_expiration_task(user_id=user_instance.id)# No async_to_sync wrapper needed

        except Exception as e:
            print("An error occurred:", e)
        
        try: 
            send_explore_locations_ready(user_id=user_instance.id)
                            
        except Exception as e:
            logger.error(f"Error occurred while sending explore locations: {str(e)}")
            # Optionally, you can return an error message or just pass to continue
            pass

        send_clear_message(user_id=user_instance.id)
        return "Success: Search completed!"
                
 
 


@shared_task(bind=True, max_retries=3)
def process_climate_twin_request(self, user_id, user_address):
    
    logger.info("Task to process climate twin request received.")
    
    print("Task to process climate twin request sent.")

    #user_instance = BadRainbowzUser.objects.get(pk=user_id)

    try:
        run_climate_twin_algorithms_task(user_id, user_address)
    except Exception as exc:
        logger.error(f"Error processing climate twin request: {exc}. Retrying...")
        raise self.retry(exc=exc)
    
    logger.info("Task to process climate twin request completed.")
    return "Request sent for processing"

@shared_task(bind=True, max_retries=3)
def schedule_expiration_task(self, user_id):

 

    try:
        # Fetch the current location for the user
        current_location = CurrentLocation.objects.get(user_id=user_id)

        
        print(current_location)

        # Ensure the location is not already expired
        if current_location.expired:
            logger.info(f"User {user_id}'s current location is already expired.")
            return "Location is already expired."
        print(f"User {user_id}'s current location is not expired.")

        # Get the last accessed time (in UTC)
        last_accessed = current_location.last_accessed

        # Ensure last_accessed is in UTC time (timezone-aware)
       # last_accessed = timezone.make_aware(last_accessed, timezone.utc)

        # Calculate the time when the expiration should happen (2 hours after last_accessed)
        expiration_time = last_accessed + timezone.timedelta(hours=2)

        # Check if the expiration task for this user already exists and cancel it
        cache_key = f"expiration_task_{user_id}"
        print(f"expiration_task_{user_id}")
        existing_task = cache.get(cache_key)
        
        if existing_task:
            # Cancel the existing task, if any (this is pseudo-code, Celery doesn't support direct cancellation)
            logger.info(f"Cancelling existing expiration task for user {user_id}")

        # Schedule a new task to update the 'expired' field after 2 hours
        logger.info(f"Scheduling expiration task for user {user_id} in 2 hours")
        print(f"Scheduling expiration task for user {user_id} in 2 hours")

        #process_expiration_task.apply_async((user_id,), countdown=600)  # 10 seconds for testing

        # Use countdown to schedule the task to run in 2 hours
        process_expiration_task.apply_async((user_id,), countdown=60)  # 2 hours in seconds
 
        timeout_seconds = max(0, (expiration_time - timezone.now()).total_seconds())
 
        cache.set(cache_key, True, timeout=int(timeout_seconds))


    except CurrentLocation.DoesNotExist:
        logger.error(f"CurrentLocation for user {user_id} does not exist.")
        print(f"CurrentLocation for user {user_id} does not exist.")

    except Exception as exc:
        logger.error(f"Error processing expiration request: {exc}. Retrying...")
        self.retry(exc=exc)
    
    logger.info("Task to process expiration request completed.")
    return "Expiration task scheduled and expired field updated."



@shared_task
def process_expiration_task(user_id):
    try:
        # Fetch the current location for the user
        current_location = CurrentLocation.objects.get(user_id=user_id)

        # Ensure the location is not already expired
        if current_location.expired:
            logger.info(f"User {user_id}'s current location is already expired.")
            print(f"User {user_id}'s current location is already expired.")
            return "Location is already expired."

        # Mark the location as expired
        current_location.expired = True
        current_location.save()
        logger.info(f"User {user_id}'s location expired successfully.")
        print(f"User {user_id}'s location expired successfully.")

    except CurrentLocation.DoesNotExist:
        logger.error(f"CurrentLocation for user {user_id} does not exist.")
    except Exception as exc:
        logger.error(f"Error processing expiration: {exc}")
        print(f"Error processing expiration: {exc}")

    return "Expiration task processed successfully."