from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
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


class ClimateTwinConsumer(AsyncWebsocketConsumer):

    from rest_framework_simplejwt.tokens import AccessToken

    async def connect(self):
        self.group_name = 'climate_updates'  
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Authenticate the user
        self.user = await self.authenticate_user()

        # Send a message indicating whether the user was retrieved
        if self.user:
            await self.accept()  # Ensure the connection is accepted before sending messages
            logger.info("Coordinates WebSocket connection established")
            await self.send(text_data=json.dumps({
                'message': f"User retrieved: {self.user}"
            }))
        else:
            await self.accept() 
            logger.info("Coordinates WebSocket connection established with demo user")
            await self.send(text_data=json.dumps({
                'message': "Demo user used as authentication failed"
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info("WebSocket connection closed")

    async def update_coordinates(self, event):
        logger.debug(f"Received update_coordinates event: {event}")
        await self.send(text_data=json.dumps({
            'country_name': event['country_name'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))
        logger.info(f"Received coordinates: Country - {event['country_name']}, Latitude - {event['latitude']}, Longitude - {event['longitude']}")

    async def authenticate_user(self):
        auth = self.scope.get('query_string', b'').decode()
        try:
            access_token = AccessToken(auth)
            user = await self.get_user(access_token)
            return user
        except:
            # Return a demo user with a hardcoded token
            return await self.get_demo_user()

    @database_sync_to_async
    def get_user(self, access_token):
        try:
            user_id = access_token['user_id']
            User = get_user_model()
            user = User.objects.get(id=user_id)
            return user
        except:
            return None

    @database_sync_to_async
    def get_demo_user(self):
        # Get or create a demo user with a hardcoded token
        demo_user, created = get_user_model().objects.get_or_create(username='sara')
        if created:
            # Set a demo token for the demo user
            demo_token = AccessToken.for_user(demo_user)
            # Customize token expiration or other properties if needed
            # Return the demo user
            return demo_user
        else:
            # If the demo user already exists, just return it
            return demo_user
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