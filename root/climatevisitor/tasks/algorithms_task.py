from ..animations import update_animation
from ..consumer import ClimateTwinConsumer  

from climatevisitor.tasks.tasks import send_location_update_to_celery, send_is_pending_location_update_to_celery, send_search_for_ruins_initiated, send_no_ruins_found, send_explore_locations_ready, send_clear_message, send_returned_home_message
from asgiref.sync import async_to_sync
from celery import shared_task, current_app, current_task
from channels.layers import get_channel_layer
from climatevisitor.climatetwinclasses.ClimateTwinFinderClass import ClimateTwinFinder
from climatevisitor.climatetwinclasses.ClimateObjectClass import ClimateObject
from climatevisitor.climatetwinclasses.ClimateEncounterClass import ClimateEncounter
from climatevisitor.climatetwinclasses.OpenMapAPIClass import OpenMapAPI
from climatevisitor.models import ClimateTwinLocation, ClimateTwinExploreLocation, CurrentLocation, ClimateTwinSearchStats
from climatevisitor import serializers


from datetime import datetime

#from datetime import timezone
from django.core.cache import cache 
from django.db import IntegrityError
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
    
    # Send location pending update to socket. Sends name: 'You are searching'
    send_is_pending_location_update_to_celery(user_id=user_id)

    # Search ends when CurrentLocation instance is saved below (instance method includes socket update)

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

        climate_twin_location_instance.save()

        try:
            climate_twin_search_stats_instance = ClimateTwinSearchStats(
                user=user_instance,
                home_temperature=climate_places.home_temperature,
                home_address=climate_places.address,
                climate_twin_temperature=climate_places.climate_twin_temperature,
                climate_twin_address=climate_places.climate_twin_address,
                points_searched_on_land=climate_places.points_generated_on_land,
                countries_searched=climate_places.countries_searched,
                total_points_generated=climate_places.points_generated,
                openweathermap_calls=climate_places.key_count,
                google_map_calls=climate_places.google_key_count,
                high_variances=climate_places.high_variance_count,
                preset_random_points_in_each_country=climate_places.preset_points_generated_in_each_country,
                preset_temp_diff_is_high_variance=climate_places.preset_temp_diff_is_high_variance,
                preset_num_high_variances_allowed=climate_places.preset_num_high_variances_allowed,
                preset_divider_for_point_gen_deviation=climate_places.preset_divider_for_point_gen_deviation,
                preset_num_final_candidates_required=climate_places.preset_num_final_candidates_required,
                home_latitude=climate_places.origin_lat,
                home_longitude=climate_places.origin_lon,
                climate_twin_latitude=climate_places.climate_twin_lat,
                climate_twin_longitude=climate_places.climate_twin_lon,
                associated_location=climate_twin_location_instance,
            )

            # Save the instance to the database
            climate_twin_search_stats_instance.save()
            logger.info("Climate Twin Search Stats instance created and saved successfully.")

        except IntegrityError as e:
            logger.error(f"Database integrity error occurred while saving Climate Twin Search Stats: {e}")
        except Exception as e:
            logger.error(f"An error occurred while creating Climate Twin Search Stats: {e}")
 
        
        user_visit_instance = UserVisit(user=user_instance, location_name=climate_twin_weather_profile.name,
                                        location_latitude=climate_twin_weather_profile.latitude,
                                         location_longitude=climate_twin_weather_profile.longitude)
        
 
        user_visit_instance.save()

        # Create the first current location and set expiration task; 
        # schedule_expiration_task will pass in the last_accessed string to the async task so that
        # that task can verify it was meant for the CurrentLocation before setting expired to True
        try:

            # This method now includes send_location_update_to_celery in order to send update every time new current location is chosen
            current_location = CurrentLocation.update_or_create_location(user=user_instance, twin_location=climate_twin_location_instance)
            
            # last_accessed_str = current_location.last_accessed.isoformat()


            # send_location_update_to_celery(user_id=user_instance.id, 
            #                                location_id=current_location.twin_location.id, # = location_visiting_id
            #                                temperature=current_location.twin_location.temperature, 
            #                                name=current_location.twin_location.name, 
            #                                latitude=current_location.twin_location.latitude, 
            #                                longitude=current_location.twin_location.longitude,
            #                                last_accessed=last_accessed_str)

            
             # Schedule the expiration task after updating or creating the current location
            schedule_expiration_task(user_id=user_instance.id)# No async_to_sync wrapper needed

        except Exception as e:
            print("An error occurred:", e)

        # try:
        #     explore_location_instance = ClimateTwinExploreLocation.objects.create(
        #         user=user_instance,
        #         twin_location=climate_twin_location_instance,
        #         created_on=timezone.now()  # Set creation time to current time
        #     )

        #     explore_location_instance.save()


        # except Exception as e:
        #     print("An error occurred:", e)
        #     # added this to abort if error
        #     return

 
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

            serializer = serializers.ClimateTwinDiscoveryLocationCreateSerializer(data=formatted_ruin)
            if serializer.is_valid():
                discovery_location_instance = serializer.save(
                    user=user_instance  
                )
                print("Success: Discovery Location saved.")
            else:
                # Handle invalid data
                print("Error: Discovery Location could not be saved.")
 
 
        
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
def schedule_expiration_task(self, user_id, duration_seconds=3600, always_send_socket_update=False): #default
    try: 
        current_location = CurrentLocation.objects.get(user_id=user_id)
 
 
        if current_location.expired and not always_send_socket_update:
            logger.info(f"User {user_id}'s current location is already expired.")
            return "Location is already expired."
        print(f"User {user_id}'s current location is not expired.")
 
        last_accessed = current_location.last_accessed 

    # I moved this up here to try to get it to activate more quickly
    # no longer using parent function for immediate expirations, can remove below once i'm sure the new approach works
        if always_send_socket_update:
            process_immediate_expiration_task.apply_async((user_id,)) # last_accessed,))  # Runs immediately


        expiration_time = last_accessed + timezone.timedelta(seconds=duration_seconds)
 
        cache_key = f"expiration_task_{user_id}"
        print(f"expiration_task_{user_id}")
        existing_task = cache.get(cache_key)
        
        if existing_task:
            # Is it possible to cancel tasks? This won't run but I would rather just cancel it directly if that is possible
            logger.info(f"Found existing expiration task for user {user_id} that will no longer get triggered (I think)")
 
        logger.info(f"Scheduling expiration task for user {user_id} in {duration_seconds} seconds")
        print(f"Scheduling expiration task for user {user_id} in {duration_seconds} seconds")
 
        if not always_send_socket_update:
            process_expiration_task.apply_async((user_id, last_accessed,), countdown=duration_seconds)  
   
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
def process_expiration_task(user_id, last_accessed):
    try: 
        current_location = CurrentLocation.objects.get(user_id=user_id)
 
        if current_location.expired:
            logger.info(f"User {user_id}'s current location is already expired.")
            print(f"User {user_id}'s current location is already expired.")
            return "Location is already expired."
 
        if last_accessed == current_location.last_accessed:
            current_location.expired = True
            current_location.save()
            logger.info(f"User {user_id}'s location expired successfully.")
            print(f"User {user_id}'s location expired successfully.")


            try:
                send_returned_home_message(user_id=user_id)
            except Exception as e:
                print(f"Couldn't send returned home message.")

            try:
                send_location_update_to_celery(user_id=user_id, location_id=None, name="You are home", temperature=None, latitude=None, longitude=None, last_accessed=None)
            except Exception as e:
                print(f"Couldn't send returned home message.")

        else:
            logger.info(f"Expiration task no longer applicable -- location has changed.")
            print(f"Expiration task no longer applicable -- location has changed.")

    except CurrentLocation.DoesNotExist:
        logger.error(f"CurrentLocation for user {user_id} does not exist.")
    except Exception as exc:
        logger.error(f"Error processing expiration: {exc}")
        print(f"Error processing expiration: {exc}")

    return "Expiration task processed successfully."



@shared_task
def process_immediate_expiration_task(user_id): 
    try: 
        current_location = CurrentLocation.objects.get(user_id=user_id) 
 
        if current_location.expired:
            logger.info(f"User {user_id}'s current location confirmed expired, celery task is sending location update.")
            print(f"User {user_id}'s current location confirmed expired, celery task is sending location update")
        
            try:
                send_returned_home_message(user_id=user_id)
            except Exception as e:
                print(f"Couldn't send returned home message.")

            try:
                send_location_update_to_celery(user_id=user_id, location_id=None, name="You are home", temperature=None, latitude=None, longitude=None, last_accessed=None)
            except Exception as e:
                print(f"Couldn't send returned home message.") 
        else:
            logger.info(f"User {user_id}'s current location not expired, celery task will not send location upcate")
            print(f"User {user_id}'s current location not expired, celery task will not send location upcate")
            return 

    except CurrentLocation.DoesNotExist:
        logger.error(f"CurrentLocation for user {user_id} does not exist.")
    except Exception as exc:
        logger.error(f"Error processing expiration: {exc}")
        print(f"Error processing expiration: {exc}")

    return "Expiration task processed successfully."