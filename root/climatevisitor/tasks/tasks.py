# tasks.py

from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..animations import update_animation
from ..consumer import ClimateTwinConsumer, LocationUpdateConsumer

# Name currently inaccurate; this is getting processed by main server
@shared_task
def send_coordinate_update_to_celery(country_name, latitude, longitude):
    # Call the function to update animation with the given coordinates
    update_animation(latitude, longitude)
    print("Sent coords to animation")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'climate_updates',  # Name of the group your consumer is listening to
        {
            'type': 'update_coordinates',  # Name of the consumer method to call
            'country_name': country_name,
            'latitude': latitude,
            'longitude': longitude,
        }
    )
    print(f"Sending Twin Finder location update: {country_name}, {latitude}, {longitude}")

    # Call the consumer method directly for testing purposes

@shared_task
def send_location_update_to_celery(name, latitude, longitude):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'location_update',
        {
            'type': 'update_location',
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
        }
    )
    