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

 
def updateAnimation(latitude, longitude):
        
        pass

class ClimateTwinConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'climate_updates'  
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
             'country_name': event['country_name'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))

     
        logger.info(f"Received coordinates: Country - {event['country_name']}, Latitude - {event['latitude']}, Longitude - {event['longitude']}")



