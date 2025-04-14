# tasks.py

from celery import shared_task
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from asgiref.sync import async_to_sync
from ..animations import update_animation
import logging
import time
from climatevisitor.send_utils import cache_and_push_notif_location_update, cache_and_push_notif_new_gift
from climatevisitor.send_utils import cache_and_push_notif_accepted_gift, cache_and_push_notif_friend_request, cache_and_push_notif_friend_request_accepted
from climatevisitor.send_utils import cache_twin_search_progress

logger = logging.getLogger(__name__)


# Name currently inaccurate; this is getting processed by main server
# Testing passing in user


# PUSH NOTIFICATIONS TRIGGERED HERE DO NOT DEPEND ON WEBSOCKET CONNECTION REMAINING OPEN

@shared_task
def send_coordinate_update_to_celery(user_id, country_name, temp_difference, temperature, latitude, longitude):

    channel_layer = get_channel_layer()
     
    group_name = f'climate_updates_{user_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,  
        {
            'type': 'update_coordinates',  
            'country_name': country_name,
            'temperature': temperature,
            'temp_difference': temp_difference,
            'latitude': latitude,
            'longitude': longitude,
        }
    )
    # Helpful to watch algorithm in real time in console, but I think is affecting performance
   # print(f"Sending Twin Finder location update: {country_name}, {temperature} degrees F, {temp_difference} degrees off, {latitude}, {longitude}")


@shared_task
def send_twin_location_search_progress_update(user_id, progress_percentage):
    
    channel_layer = get_channel_layer()
    group_name = f'location_update_{user_id}'

    cache_twin_search_progress(user_id, progress_percentage)

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'twin_location_search_progress_update',
            'search_progress': f'{progress_percentage}',
        }
    ) 

@shared_task
def reset_twin_location_search_progress_update(user_id):

    progress_percentage='00.0'
    
    channel_layer = get_channel_layer()
    group_name = f'location_update_{user_id}'

    cache_twin_search_progress(user_id, progress_percentage)

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'twin_location_search_progress_update',
            'search_progress': f'{progress_percentage}',
        }
    ) 



@shared_task
def send_gift_notification(user_id, user_username, recipient_id):
    logger.info(f"send_gift_notification triggered for user_id: {user_id}, recipient_id: {recipient_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    cache_and_push_notif_new_gift(user_id, user_username, recipient_id)

    notification_message = f'{user_username} sent you a treasure!'
    # sending clear method will remove the notification, if I remember correctly

 
    
    try: 
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'gift_notification',
                'notification': notification_message,
            }
        )
        logger.info(f"Notification successfully sent to {group_name}")
    except Exception as e:
        logger.error(f"Failed to send notification to {group_name}: {e}")
     

@shared_task
def send_gift_accepted_notification(user_id, user_username, recipient_id):
    logger.info(f"send_gift_accepted_notification triggered for user_id: {user_id}, recipient_id: {recipient_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    notification_message = f'User ID {user_id} accepted your gift!'

    cache_and_push_notif_accepted_gift(user_id, user_username, recipient_id)


    
    try: 
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'gift_notification',
                'notification': notification_message,
            }
        )
        logger.info(f"Notification successfully sent to {group_name}")
    except Exception as e:
        logger.error(f"Failed to send notification to {group_name}: {e}")
     

@shared_task
def send_friend_request_notification(user_id, user_username, recipient_id):
    logger.info(f"send_friend_request_notification triggered for user_id: {user_id}, recipient_id: {recipient_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    
    #Sending clear message will remove 
    cache_and_push_notif_friend_request(user_id, user_username, recipient_id)

    notification_message = f'User ID {user_id} wants to be friends!'
    
    try: 
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'friend_notification',
                'notification': notification_message,
            }
        )
        logger.info(f"Notification successfully sent to {group_name}")
    except Exception as e:
        logger.error(f"Failed to send notification to {group_name}: {e}")



@shared_task
def send_friend_request_accepted_notification(user_id, user_username, recipient_id):
    logger.info(f"send_friend_request_notification triggered for user_id: {user_id}, recipient_id: {recipient_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    # believe this gets cleared by sending clear message, same as above
    cache_and_push_notif_friend_request_accepted(user_id, user_username, recipient_id)

    notification_message = f'User ID {user_id} accepted your friend request!'
    
    try: 
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'friend_notification',
                'notification': notification_message,
            }
        )
        logger.info(f"Notification successfully sent to {group_name}")
    except Exception as e:
        logger.error(f"Failed to send notification to {group_name}: {e}")


@shared_task
def send_clear_notification_cache(user_id):
    recipient_id = user_id
    logger.info(f"send_clear_friend_request_notification triggered for user_id: {user_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    notification_message = ''

    #No time out right now, may need to remove manually once user accepts/declines message
    cache.set(f"last_notification_{recipient_id}", notification_message, timeout=3600)  # Cache for 1 hour
    logger.info(f"Notification cached for {recipient_id}: {notification_message}")


    
    try: 
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'gift_notification', #I think this works for both gift and friend notifs, they are in same place
                'notification': notification_message,
            }
        )
        logger.info(f"Notification successfully sent to {group_name}")
    except Exception as e:
        logger.error(f"Failed to send notification to {group_name}: {e}")


@shared_task
def send_clear_friend_request_notification(user_id, friend_id):
    recipient_id = user_id
    logger.info(f"send_clear_friend_request_notification triggered for user_id: {user_id}, sender_id: {friend_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    notification_message = ''

    #No time out right now, may need to remove manually once user accepts/declines message
    cache.set(f"last_notification_{recipient_id}", notification_message, timeout=3600)  # Cache for 1 hour
    logger.info(f"Notification cached for {recipient_id}: {notification_message}")


    
    try: 
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'friend_notification',
                'notification': notification_message,
            }
        )
        logger.info(f"Notification successfully sent to {group_name}")
    except Exception as e:
        logger.error(f"Failed to send notification to {group_name}: {e}")




@shared_task
def send_clear_gift_notification(user_id, friend_id):
    recipient_id = user_id
    logger.info(f"send_clear_gift_notification triggered for user_id: {user_id}, sender_id: {friend_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    notification_message = ''

    #No time out right now, may need to remove manually once user accepts/declines message
    cache.set(f"last_notification_{recipient_id}", notification_message, timeout=3600)  # Cache for 1 hour
    logger.info(f"Notification cached for {recipient_id}: {notification_message}")


    
    try: 
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'gift_notification',
                'notification': notification_message,
            }
        )
        logger.info(f"Notification successfully sent to {group_name}")
    except Exception as e:
        logger.error(f"Failed to send notification to {group_name}: {e}")





@shared_task
def send_is_pending_location_update_to_celery(user_id):
     
    pending_message = 'You are searching' 

    logger.info(f"Preparing to send pending location update to Celery with data: "
                f"user_id: {user_id}, name: 'You are searching'")

    try:
        channel_layer = get_channel_layer()

        group_name = f'location_update_{user_id}'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'update_location',
                'state': 'searching for twin',
                'base_location': None,
                'location_id': None,
                'location_same_as_last_update': None,
                'name': pending_message,
                'temperature': None,
                'latitude': None,
                'longitude': None,
                'last_accessed': None,
            }
        )
 
        logger.info(f"Location update sent successfully for user_id: {user_id}, name: {pending_message}")

    except Exception as e: 
        logger.error(f"Error in send_location_update_to_celery task for user_id: {user_id}, name: {pending_message}. "
                     f"Error: {str(e)}")
        # tbh gpty gave this type of error to me and I'm not sure if it is necessary
        raise SuspiciousOperation(f"Error sending location update to Celery: {str(e)}")

 






@shared_task
def send_location_update_to_celery(user_id, state, base_location, location_id, location_same_as_last_update, name, temperature, latitude, longitude, last_accessed):
     
    logger.info(f"Preparing to send location update to Celery with data: "
                f"user_id: {user_id}, state: {state}, base_location: {base_location}, location_id: {location_id}, "
                f"name: {name}, temperature: {temperature}, latitude: {latitude}, "
                f"longitude: {longitude}, last_accessed: {last_accessed}")

    try:
        channel_layer = get_channel_layer()

        group_name = f'location_update_{user_id}'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'update_location',
                'state': state,
                'base_location': base_location,
                'location_id': location_id,
                'location_same_as_last_update': location_same_as_last_update,
                'name': name,
                'temperature': temperature,
                'latitude': latitude,
                'longitude': longitude,
                'last_accessed': last_accessed,
            }
        )

       
        logger.info(f"Location update sent successfully for user_id: {user_id}, location_id: {location_id}")

    except Exception as e:
        logger.warning(f"No active connection for user_id: {user_id}, or failed to send via channel layer. Error: {str(e)}")

    
    # Push notification is inside this
    cache_and_push_notif_location_update(user_id, state, base_location, location_id, name, latitude, longitude, last_accessed)
    
    logger.info(f"Location update complete for user_id: {user_id}, location_id: {location_id}")
 

# Not a Celery task but goes with them
# Cache should fail silently but added try/except anyway
def extra_coverage_cache_location_update(user_id, state, base_location, location_id, name, latitude, longitude, last_accessed):
    cache_key = f"current_location_{user_id}"
    logger.debug(f"Extra coverage caching current location for user {user_id} with key: {cache_key}")

    location_data = {
        'state' : state,
        'base_location': base_location,
        'location_id': location_id,
        'location_same_as_last_update': None,
        'name': name,
        'latitude': latitude,
        'longitude': longitude,
        'last_accessed': last_accessed,
    }

    try:
        cache.set(cache_key, location_data)
        logger.debug(f"Successfully cached location for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to cache location for user {user_id}: {str(e)}")


# Not a Celery task but goes with them
# Cache to temporarily store current location when searching for new
# fall back to in case of search fail


def save_current_location_to_backup_cache(user_id):
    cache_key = f"current_location_{user_id}"
    backup_cache_key = f"current_location_backup_{user_id}"
    current_location_cache = cache.get(cache_key)
 
    if current_location_cache and 'location_id' in current_location_cache and 'last_accessed' in current_location_cache:
        
        logger.info(f"Backing up current location cache for user {user_id}")
        
        backup_data = {
            'state': current_location_cache.get('state'),
            'base_location': current_location_cache.get('base_location'),
            'location_id': current_location_cache.get('location_id'),
            'location_same_as_last_update': current_location_cache.get('location_same_as_last_update', None),
            'name': current_location_cache.get('name', 'Error getting location name'),  
            'latitude': current_location_cache.get('latitude'),
            'longitude': current_location_cache.get('longitude'),
            'last_accessed': current_location_cache.get('last_accessed')
        } 

        if None not in (backup_data['location_id'], backup_data['latitude'], backup_data['longitude']):
            cache.set(backup_cache_key, backup_data)  
            logger.info(f"Backup cache set for user {user_id}: {backup_data}")
        else:
            logger.warning(f"Skipping backup for user {user_id}, missing critical fields: {backup_data}")

    else:
        logger.warning(f"No valid location data found in cache for user {user_id}")


def restore_location_from_backup_cache_and_send_update(user_id):
    backup_cache_key = f"current_location_backup_{user_id}"
    cache_key = f"current_location_{user_id}"
    backup_location_cache = cache.get(backup_cache_key)
 
    if backup_location_cache and 'location_id' in backup_location_cache and 'last_accessed' in backup_location_cache:
        
        logger.info(f"Restoring location from backup cache for user {user_id}")
        
        location_data = {
            'state': backup_location_cache.get('state'),
            'base_location': backup_location_cache.get('base_location'),
            'location_id': backup_location_cache.get('location_id'),
            'location_same_as_last_update': backup_location_cache.get('location_same_as_last_update'),
            'name': backup_location_cache.get('name', 'Error getting location name'),  
            'latitude': backup_location_cache.get('latitude'),
            'longitude': backup_location_cache.get('longitude'),
            'last_accessed': backup_location_cache.get('last_accessed')
        } 

        try:
            channel_layer = get_channel_layer()

            group_name = f'location_update_{user_id}'

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'update_location',
                    'state': backup_location_cache.get('state', 'Error getting location state'),
                    'base_location': backup_location_cache.get('base_location'),
                    'location_id': backup_location_cache.get('location_id'),
                    'location_same_as_last_update': backup_location_cache.get('location_same_as_last_update'),
                    'name': backup_location_cache.get('name', 'Error getting location name'),  
                    'temperature': None,
                    'latitude': backup_location_cache.get('latitude'),
                    'longitude': backup_location_cache.get('longitude'),
                    'last_accessed': backup_location_cache.get('last_accessed')
                }
            )
    
            logger.info(f"Location update sent successfully for user_id: {user_id}")

        except Exception as e: 
            logger.error(f"Error in send_location_update_to_celery task for user_id: {user_id}. "
                        f"Error: {str(e)}")
            # tbh gpty gave this type of error to me and I'm not sure if it is necessary
            raise SuspiciousOperation(f"Error sending location update to Celery: {str(e)}")
    
                
        if None not in (location_data['location_id'], location_data['latitude'], location_data['longitude']):
            cache.set(cache_key, location_data)  
            logger.info(f"Location cache set for user {user_id}: {location_data}")
        else:
            logger.warning(f"Skipping backup for user {user_id}, missing critical fields: {location_data}")

    else:
        logger.warning(f"No valid location data found in backup cache for user {user_id}")


