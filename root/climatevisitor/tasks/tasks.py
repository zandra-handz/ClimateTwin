# tasks.py

from celery import shared_task
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from asgiref.sync import async_to_sync
from ..animations import update_animation
import logging
import time


logger = logging.getLogger(__name__)


# Name currently inaccurate; this is getting processed by main server
# Testing passing in user



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
    print(f"Sending Twin Finder location update: {country_name}, {temperature} degrees F, {temp_difference} degrees off, {latitude}, {longitude}")


@shared_task
def send_search_for_ruins_initiated(user_id):
    channel_layer = get_channel_layer()

    group_name = f'location_update_{user_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'search_for_ruins',
            'message': 'Searching for ruins!',
        }
    ) 


@shared_task
def send_returned_home_message(user_id):
    time.sleep(8)
    channel_layer = get_channel_layer()

    group_name = f'location_update_{user_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'returned_home_message',
            'message': 'User has returned home.',
        }
    ) 



@shared_task
def send_clear_message(user_id):
    time.sleep(8)
    channel_layer = get_channel_layer()

    group_name = f'location_update_{user_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'clear_message',
            'message': 'Clear',
        }
    ) 





@shared_task
def send_explore_locations_ready(user_id):
    channel_layer = get_channel_layer()

    group_name = f'location_update_{user_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'explore_locations_ready',
            'message': 'Search complete!',
        }
    ) 




@shared_task
def send_no_ruins_found(user_id):
    channel_layer = get_channel_layer()

    group_name = f'location_update_{user_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'no_ruins_found',
            'message': 'No ruins found',
        }
    ) 




@shared_task
def send_gift_notification(user_id, recipient_id):
    logger.info(f"send_gift_notification triggered for user_id: {user_id}, recipient_id: {recipient_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    notification_message = f'User ID {user_id} sent you a treasure!'

    #No time out right now, may need to remove manually once user accepts/declines message
    cache.set(f"last_notification_{recipient_id}", notification_message) #, timeout=3600)  # Cache for 1 hour
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
def send_gift_accepted_notification(user_id, recipient_id):
    logger.info(f"send_gift_accepted_notification triggered for user_id: {user_id}, recipient_id: {recipient_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    notification_message = f'User ID {user_id} accepted your gift!'

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
def send_friend_request_notification(user_id, recipient_id):
    logger.info(f"send_friend_request_notification triggered for user_id: {user_id}, recipient_id: {recipient_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    notification_message = f'User ID {user_id} wants to be friends!'

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
def send_friend_request_accepted_notification(user_id, recipient_id):
    logger.info(f"send_friend_request_notification triggered for user_id: {user_id}, recipient_id: {recipient_id}")

    channel_layer = get_channel_layer()
    group_name = f'location_update_{recipient_id}'
    
    logger.info(f"Attempting to send message to group: {group_name}")

    notification_message = f'User ID {user_id} accepted your friend request!'

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
def send_location_update_to_celery(user_id, location_id, name, temperature, latitude, longitude, last_accessed):
     
    logger.info(f"Preparing to send location update to Celery with data: "
                f"user_id: {user_id}, location_id: {location_id}, "
                f"name: {name}, temperature: {temperature}, latitude: {latitude}, "
                f"longitude: {longitude}, last_accessed: {last_accessed}")

    try:
        channel_layer = get_channel_layer()

        group_name = f'location_update_{user_id}'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'update_location',
                'location_id': location_id,
                'name': name,
                'temperature': temperature,
                'latitude': latitude,
                'longitude': longitude,
                'last_accessed': last_accessed,
            }
        )
 
        logger.info(f"Location update sent successfully for user_id: {user_id}, location_id: {location_id}")

    except Exception as e: 
        logger.error(f"Error in send_location_update_to_celery task for user_id: {user_id}, location_id: {location_id}. "
                     f"Error: {str(e)}")
        # tbh gpty gave this type of error to me and I'm not sure if it is necessary
        raise SuspiciousOperation(f"Error sending location update to Celery: {str(e)}")