# tasks.py

from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..animations import update_animation
from ..consumer import ClimateTwinConsumer  


@shared_task
def send_coordinate_update_to_celery(latitude, longitude):
    # Call the function to update animation with the given coordinates
    update_animation(latitude, longitude)
    print("Sent coords to animation")
    channel_layer = get_channel_layer()
    print(channel_layer)
    async_to_sync(channel_layer.group_send)(
        'climate_updates',  # Name of the group your consumer is listening to
        {
            'type': 'update_coordinates',  # Name of the consumer method to call
            'latitude': latitude,
            'longitude': longitude,
        }
    )
    print(f"Sending update for coordinate pair: {latitude}, {longitude}")

    # Call the consumer method directly for testing purposes

