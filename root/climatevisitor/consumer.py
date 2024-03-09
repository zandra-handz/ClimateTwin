from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
import json
import logging
from .views import CurrentExploreLocationView

logger = logging.getLogger(__name__)

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



class LocationUpdateConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'location_update'  
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        logger.info("Location Update WebSocket connection established")
        self.accept()
        

    def disconnect(self, close_code):

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        logger.info("Location Update WebSocket connection closed")
        

    def update_location(self, event):

        logger.debug(f"Received update_locations event: {event}")
        self.send(text_data=json.dumps({
             'name': event['name'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))

     
        logger.info(f"Received location update: Location - {event['name']}, Latitude - {event['latitude']}, Longitude - {event['longitude']}")


    def current_location(self, event):
        logger.debug(f"Received update_location event from Celery: {event}")
        
        # Use the view function to get the latest explore location
        latest_location = CurrentExploreLocationView().get_latest_explore_location(self.scope['user'])
        
        if latest_location:
            # If a latest location is found, send it through the WebSocket
            self.send(text_data=json.dumps({
                'type': 'current_location',
                'name': 'Latest Explore Location',
                'latitude': latest_location.latitude,
                'longitude': latest_location.longitude,
            }))
            logger.info("Sent latest explore location through WebSocket")
        else:
            # If no latest location is found, handle it accordingly
            logger.info("No latest explore location found")