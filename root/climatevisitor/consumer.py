import json
import logging
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

# Configure logger to print to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


 # JavaScript function to update dots on canvas
def updateAnimation(latitude, longitude):
        # Your JavaScript code to update dots on canvas here
        pass

class ClimateTwinConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'climate_updates'  # Group name
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        logger.info("WebSocket connection established")
        self.accept()
        

    def disconnect(self, close_code):

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        logger.info("WebSocket connection closed")
        

    def update_coordinates(self, event):

        logger.debug(f"Received update_coordinates event: {event}")
        self.send(text_data=json.dumps({
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))

        # Additional logging for debugging
        logger.info(f"Received coordinates: Latitude - {event['latitude']}, Longitude - {event['longitude']}")

        # Has own JS file
        #latitude = event['latitude']
        #longitude = event['longitude']
        #updateAnimation(latitude, longitude)  # Call JavaScript function to update dots on canvas

        # Additional logging for debugging
        logger.info(f"Received coordinates: Latitude - {event['latitude']}, Longitude - {event['longitude']}")


