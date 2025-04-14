from ..animations import update_animation
from ..consumer import ClimateTwinConsumer  

from climatevisitor.tasks.tasks import send_location_update_to_celery, send_is_pending_location_update_to_celery, save_current_location_to_backup_cache, restore_location_from_backup_cache_and_send_update
from asgiref.sync import async_to_sync
from celery import shared_task, current_app, current_task
from channels.layers import get_channel_layer
from climatevisitor.climatetwinclasses.ClimateTwinFinderClass import ClimateTwinFinder
from climatevisitor.climatetwinclasses.ClimateObjectClass import ClimateObject
from climatevisitor.climatetwinclasses.ClimateEncounterClass import ClimateEncounter
from climatevisitor.climatetwinclasses.OpenMapAPIClass import OpenMapAPI
from climatevisitor.models import ClimateTwinLocation, HomeLocation, CurrentLocation, ClimateTwinSearchStats
from climatevisitor import serializers

from climatevisitor.send_utils import push_expiration_task_scheduled, push_expiration_task_executed
from climatevisitor.send_utils import  check_for_twin_search_lock, push_warning_location_expiring_soon, check_and_set_twin_search_lock, remove_twin_search_lock

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
    
    save_current_location_to_backup_cache(user_id)
    # Send location pending update to socket. Sends name: 'You are searching'
    send_is_pending_location_update_to_celery(user_id=user_id)

    # Search ends when CurrentLocation instance is saved below (instance method includes socket update)

    climate_places = ClimateTwinFinder(user_id_for_celery=user_id, address=user_address)
    
    if climate_places:
        print(f"Twin Location found: {climate_places.home_climate}")

    if climate_places and climate_places.home_climate:
        print("climate_places.home_climate exists -- proceeding")
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

    if climate_places and climate_places.climate_twin:
        print("climate_places.home_twin exists -- proceeding")
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
            print("Climate Twin Search Stats instance created and saved successfully.")

            logger.info("Climate Twin Search Stats instance created and saved successfully.")

        except IntegrityError as e:
            print(f"Database integrity error occurred while saving Climate Twin Search Stats: {e}")
            logger.error(f"Database integrity error occurred while saving Climate Twin Search Stats: {e}")
        
        except Exception as e:
            print(f"An error occurred while creating Climate Twin Search Stats: {e}")
 
            logger.error(f"An error occurred while creating Climate Twin Search Stats: {e}")
 
        
        user_visit_instance = UserVisit(user=user_instance, location_name=climate_twin_weather_profile.name,
                                        location_latitude=climate_twin_weather_profile.latitude,
                                         location_longitude=climate_twin_weather_profile.longitude)
        
 
        user_visit_instance.save()

        # Create the first current location and set expiration task; 
        # schedule_expiration_task will pass in the last_accessed string to the async task so that
        # that task can verify it was meant for the CurrentLocation before setting expired to True
        try:

            current_location = CurrentLocation.update_or_create_location(user=user_instance, base_location=climate_twin_location_instance, twin_location=climate_twin_location_instance)
            
            if not current_location: # If not current location, won't get ruins 
                # This and the try block in general are here to allow fallback to previous explore location
                # in case of a failure in the algo here, so that user can still keep exploring where they were
                restore_location_from_backup_cache_and_send_update(user_id)

            else:
                # need this here even though it is also seemingly in the update/create method
                last_accessed_str = current_location.last_accessed.isoformat()


                send_location_update_to_celery(user_id=user_instance.id, state='searching for ruins',
                                            base_location=current_location.base_location.id,
                                            location_id=current_location.twin_location.id, # = location_visiting_id
                                            location_same_as_last_update=None,
                                            temperature=current_location.twin_location.temperature, 
                                            name=current_location.twin_location.name, 
                                            latitude=current_location.twin_location.latitude, 
                                            longitude=current_location.twin_location.longitude,
                                            last_accessed=last_accessed_str)

            
                # Schedule the expiration task after updating or creating the current location
               
                # the create/update method schedules this
                # NEVERMIND, it doesn't work inside of teh update and create method
                # I moved it up in the View, but this doesn't ping the view, so should be fine to keep
                # here?
                schedule_expiration_task(user_id=user_instance.id)# No async_to_sync wrapper needed

                osm_api = OpenMapAPI()
                try:
                    osm_results = osm_api.find_ancient_ruins(climate_twin_weather_profile.latitude, climate_twin_weather_profile.longitude, radius=100000, num_results=15)
                    nearby_ruins = osm_api.format_ruins_with_wind_compass_for_post(osm_results, climate_twin_weather_profile.wind_direction)

                    # Not strictly necessary to check if dict, because function sets an empty dict at beginning
                    if isinstance(nearby_ruins, dict): # added 4/3/2025
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
                    
                    
                except Exception as e:
                    print(f"Error fetching OSM results: {e}")
               # osm_results = osm_api.find_ancient_ruins(climate_twin_weather_profile.latitude, climate_twin_weather_profile.longitude, radius=100000, num_results=15)
                
            
        
                
                try: 
                    # THE ONLY TIME LOCATION_SAME_AS_UPDATE will be 'yes' ( and it still caches as None)
                    # Currently this exists for the sole purpose of not causing an unnecessary rerender of FE App
                    # based on the current design
                    send_location_update_to_celery(user_id=user_instance.id, state='exploring',
                            base_location=current_location.base_location.id,
                            location_id=current_location.twin_location.id, # = location_visiting_id
                            location_same_as_last_update='yes',
                            temperature=current_location.twin_location.temperature, 
                            name=current_location.twin_location.name, 
                            latitude=current_location.twin_location.latitude, 
                            longitude=current_location.twin_location.longitude,
                            last_accessed=last_accessed_str)


                                    
                except Exception as e:
                    logger.error(f"Error occurred while sending explore locations: {str(e)}")
                    # Optionally, you can return an error message or just pass to continue
                    pass
 
                return "Success: Search completed!"
        
        except Exception as e:
            print("An error occurred:", e) 

    # Reset socket to 'home' if no climate twin location returned in ClimateTwinFinder object
    else:
        try:
            push_expiration_task_scheduled(user_id, f'Oops! Could not find a twin location. Please try searching again.')
            send_location_update_to_celery(user_id=user_id, state='home', base_location=None, location_same_as_last_update=None, location_id=None, name="You are home", temperature=None, latitude=None, longitude=None, last_accessed=None)
        except Exception as e:
            print(f"Couldn't send returned home message.")

                    
 
 

# @shared_task(bind=True, max_retries=3)
# def process_climate_twin_request(self, user_id, user_address):
    
#     logger.info("Task to process climate twin request received.")
#     print("Task to process climate twin request sent.")

    
#     lock_key = f"search_active_for_{user_id}"
#     lock_ttl = 60 * 5  # 5 minutes
 
#     if not cache.add(lock_key, "LOCKED", timeout=lock_ttl):
#         logger.warning(f"Lock already active for user {user_id}. Skipping task.")
#         return "Another request is already running."

#     try:
#         run_climate_twin_algorithms_task(user_id, user_address)
#     except Exception as exc:
#         logger.error(f"Error processing climate twin request: {exc}. Retrying...")
#         raise self.retry(exc=exc)
#     finally:
#         # Always release the lock
#         cache.delete(lock_key)  # also deleting in ExpireCurrentLocationView in case
#         # user wants to go home and immediately fire another search
    
#     logger.info("Task to process climate twin request completed.")
#     return "Request sent for processing"


@shared_task(bind=True, max_retries=3)
def process_climate_twin_request(self, user_id, user_address):
    logger.info("Task to process climate twin request received.")
    print("Task to process climate twin request sent.")

    if check_for_twin_search_lock(user_id):
    # if not check_and_set_twin_search_lock(user_id):
        logger.warning(f"Lock already active for user {user_id}. Skipping task.")
        push_expiration_task_scheduled(user_id, f'Oops! A search is already running.')
        return "Another request is already running."

    retry_exc = None

    try:
        run_climate_twin_algorithms_task(user_id, user_address)
    except Exception as exc:
        logger.error(f"Error processing climate twin request: {exc}. Retrying...")
        retry_exc = exc
    # finally:
    #     remove_twin_search_lock(user_id)
    #     logger.info(f"Deleted lock for user {user_id}")

    if retry_exc:
        raise self.retry(exc=retry_exc)

    remove_twin_search_lock(user_id)
    logger.info("Task to process climate twin request completed.")
    return "Request sent for processing"



@shared_task(bind=True, max_retries=3)
def schedule_expiration_task(self, user_id, duration_seconds=3600, always_send_socket_update=False): #default
    
    # FOR DEBUGGING:
    # push_expiration_task_scheduled(user_id, 'INITIATED')
    try: 
        current_location = CurrentLocation.objects.get(user_id=user_id)
 
 
        if current_location.expired and not always_send_socket_update:
            logger.info(f"User {user_id}'s current location is already expired.")
            return "Location is already expired."
        print(f"User {user_id}'s current location is not expired.")
 
        last_accessed = current_location.last_accessed 

        expiration_time = last_accessed + timezone.timedelta(seconds=duration_seconds)
 
        cache_key = f"expiration_task_{user_id}"
        print(f"expiration_task_{user_id}")
        existing_task = cache.get(cache_key)
        
        if existing_task:
            # Is it possible to cancel tasks? This won't run but I would rather just cancel it directly if that is possible
            logger.info(f"Found existing expiration task for user {user_id} that will no longer get triggered (I think)")
 
        logger.info(f"Scheduling expiration task for user {user_id} in {duration_seconds} seconds")
        print(f"Scheduling expiration task for user {user_id} in {duration_seconds} seconds")
  
        process_expiration_task.apply_async((user_id, last_accessed,), countdown=duration_seconds)  
   
        timeout_seconds = max(0, (expiration_time - timezone.now()).total_seconds())
 
        cache.set(cache_key, True, timeout=int(timeout_seconds))

        # FOR DEBUGGING
        # push_expiration_task_scheduled(user_id, timeout_seconds)

        process_impending_expiration_warning_task.apply_async((user_id, expiration_time, last_accessed,), countdown=3000)
        


    except CurrentLocation.DoesNotExist:
        logger.error(f"CurrentLocation for user {user_id} does not exist.")
        print(f"CurrentLocation for user {user_id} does not exist.")

    except Exception as exc:
        logger.error(f"Error processing expiration request: {exc}. Retrying...")
        self.retry(exc=exc)
    
    logger.info("Task to process expiration request completed.")
    return "Expiration task scheduled and expired field updated."


@shared_task
def process_impending_expiration_warning_task(user_id, expiration_time=None, last_accessed=None):

    if last_accessed is None or expiration_time is None: 
        print("Can't sent location exp warning message, either no last_access or expiration_time passed in to function")
        return
    
    try:
        current_location = CurrentLocation.objects.get(user_id=user_id)

        location_name = 'location'

        if current_location.twin_location:
            location_name = current_location.twin_location.name
        elif current_location.explore_location:
            location_name = current_location.explore_location.name
            
        if current_location.expired:
            return "No location exp warning message necessary, location already expired."
        
        if last_accessed == current_location.last_accessed: 

            minutes_remaining = max(0, int((expiration_time - timezone.now()).total_seconds() / 60))
            push_warning_location_expiring_soon(user_id, location_name, minutes_remaining)

    except Exception as e: 
        print(f"Couldn't send location expiration warning message.")

@shared_task
def process_expiration_task(user_id, last_accessed=None):

    if last_accessed is None:
        logger.warning(f"User {user_id} has no last_accessed timestamp, exiting process_expiration_task.")
        return

    try: 
        current_location = CurrentLocation.objects.get(user_id=user_id)
 
        if current_location.expired:
            logger.info(f"User {user_id}'s current location is already expired.")
            print(f"User {user_id}'s current location is already expired.")

            # Deleting home location will cascade-delete all the other locations except for the current location
            # To save data, we will need to save more stuff to the uservisits. 
            home_location = HomeLocation.objects.filter(user=user_id).first()
            if home_location:
                home_location.delete()
                
            return "Location is already expired."
 
        if last_accessed == current_location.last_accessed:
            current_location.expired = True
            current_location.save()

            # Deleting home location will cascade-delete all the other locations except for the current location
            # To save data, we will need to save more stuff to the uservisits. 
            home_location = HomeLocation.objects.filter(user=user_id).first()
            if home_location:
                home_location.delete()
            logger.info(f"User {user_id}'s location expired successfully.")
            
            # FOR DEBUGGING
            #push_expiration_task_executed(user_id)
            print(f"User {user_id}'s location expired successfully.")
 
            try:
                send_location_update_to_celery(user_id=user_id, state='home', base_location=None, location_same_as_last_update=None, location_id=None, name="You are home", temperature=None, latitude=None, longitude=None, last_accessed=None)
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
                send_location_update_to_celery(user_id=user_id, state='home', base_location=None, location_id=None, location_same_as_last_update=None, name="You are home", temperature=None, latitude=None, longitude=None, last_accessed=None)
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