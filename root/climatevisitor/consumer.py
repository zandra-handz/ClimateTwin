from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer

from channels.db import database_sync_to_async
from django.apps import apps
import asyncio

import json
import logging

logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

 
def updateAnimation(latitude, longitude):
        
        pass

def get_user_model():
    return apps.get_model('users', 'BadRainbowzUser')

class ClimateTwinConsumer(WebsocketConsumer):
    async def connect(self):
        
        user = await self.get_user(self.scope['user_id'])
        if user:
            await self.channel_layer.group_add(
                f'climate_updates_user_{user.id}',
                self.channel_name
            )
            await self.accept()
            # Send success message to the client
            await self.send(text_data="User successfully connected to WebSocket.")
        else:
            await self.close()

    async def disconnect(self, close_code):
        user = await self.get_user(self.scope['user_id'])
        if user:
            await self.channel_layer.group_discard(
                f'climate_updates_user_{user.id}',
                self.channel_name
            )

    async def get_user(self, user_id):
        BadRainbowzUser = get_user_model()
        # Implement your logic to retrieve the user based on user_id
        # For example, if you're using Django, you might do something like this:
        try:
            user = await database_sync_to_async(BadRainbowzUser.objects.get)(id=user_id)
            return user
        except BadRainbowzUser.DoesNotExist:
            return None

    async def receive(self, text_data):
        # Handle incoming messages here
        pass

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return BadRainbowzUser.objects.get(id=user_id)
        except BadRainbowzUser.DoesNotExist:
            return None

'''
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

'''

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
        # Send the message data directly
        self.send(text_data=json.dumps({
            'type': 'current_location',
            'name': '!! HI THIS IS A SCHEDULED TASKS TEST !!',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))
        logger.info("Received location update from Celery")