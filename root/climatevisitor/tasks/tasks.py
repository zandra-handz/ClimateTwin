# tasks.py

from celery import shared_task
from channels.layers import get_channel_layer
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
    
    logger.info(f"Sending message to group: {group_name}")

    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'gift_notification',
                'notification': 'You have been sent a treasure!',
            }
        ) 
        logger.info(f"Notification successfully sent to {group_name}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")




 





@shared_task
def send_location_update_to_celery(user_id, name, temperature, latitude, longitude):

    channel_layer = get_channel_layer()
    
    group_name = f'location_update_{user_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'update_location',
            'name': name,
            'temperature': temperature,
            'latitude': latitude,
            'longitude': longitude,
        }
    )
    