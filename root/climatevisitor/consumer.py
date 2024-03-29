from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from climatevisitor.tasks.tasks import send_location_update_to_celery

from channels.db import database_sync_to_async
from django.apps import apps
import asyncio
 

import json
import logging

from urllib.parse import parse_qs


logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

import requests

 
#def updateAnimation(latitude, longitude):
        
#        pass



def get_user_model():
    return apps.get_model('users', 'BadRainbowzUser')

class ClimateTwinConsumer(WebsocketConsumer):
    def connect(self):

        self.user_id = 3  # demo User ID is hardcoded for right now

        self.group_name = f'climate_updates_{self.user_id}'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        ) 

        
        self.user = self.authenticate_user()
 
        if self.user:
            self.accept() 
            # logger.info("Coordinates WebSocket connection established")
            self.send(text_data=json.dumps({
                'message': f"User retrieved: {self.user}"
            }))
        else:
            self.accept()
            # logger.info("Coordinates WebSocket connection established with demo user")
            self.send(text_data=json.dumps({
                'message': "Demo user used as authentication failed"
            }))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        # logger.info("WebSocket connection closed")

    def update_coordinates(self, event):
        # logger.debug(f"Received update_coordinates event: {event}")
        self.send(text_data=json.dumps({
            'country_name': event['country_name'],
            'temperature': event['temperature'],
            'temp_difference': event['temp_difference'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))
        # logger.info(f"Received coordinates: Country - {event['country_name']}, Temperature - {event['temperature']}, Latitude - {event['latitude']}, Longitude - {event['longitude']}")

    def authenticate_user(self):
        auth = self.scope.get('query_string', b'').decode()
        user_token = parse_qs(auth).get('user_token', [None])[0]
        if user_token:
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                access_token = AccessToken(user_token)
                user = self.get_user(access_token)
                return user
            except:
                # Return a demo user with a hardcoded token
                return self.get_demo_user()
        else:
            # Return a demo user with a hardcoded token
            return self.get_demo_user()

    def get_user(self, access_token):
        try:
            user_id = access_token['user_id']
            user = self.get_user_model().objects.get(id=user_id)
            return user
        except:
            return None

    def get_demo_user(self):
        # Get or create a demo user with a hardcoded token
        try:
            demo_user = self.get_user_model().objects.get(username='sara')

            from rest_framework_simplejwt.tokens import AccessToken
            demo_token = AccessToken.for_user(demo_user)
            
            logger.debug(f"ClimateTwinConsumer generated JWT token: {demo_token}")
            
            return demo_user
        except self.get_user_model().DoesNotExist:
            # Log the error
            # logger.error("Demo user 'sara' does not exist.")
                
            # Raise an error
            raise Exception("Demo user 'sara' does not exist.")

    @staticmethod
    def get_user_model():
        return apps.get_model('users', 'BadRainbowzUser')



class LocationUpdateConsumer(WebsocketConsumer):

    def connect(self):

        self.user_id = 3

        self.group_name = f'location_update_{self.user_id}'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        #self.user = self.authenticate_user()
        self.user, self.token = self.authenticate_user() 
        # logger.info(f"Location Update Websockey connecting with user: {self.user}, token: {self.token}")

        self.accept()
        # logger.info("Location Update WebSocket connection established")

        data = self.fetch_data_from_endpoint(self.token)
        
        self.update_location(data)
        # logger.info(data) 

        # send_location_update_to_celery.delay(self.user_id, data['name'], data['temperature'], data['latitude'], data['longitude'])




    def fetch_data_from_endpoint(self, token):
        # Fetch data from endpoint(s)
        explore_data_endpoint = 'https://climatetwin-lzyyd.ondigitalocean.app/climatevisitor/currently-exploring/'
        discovery_locations_endpoint = 'https://climatetwin-lzyyd.ondigitalocean.app/climatevisitor/locations/nearby/'
        twin_endpoint = 'https://climatetwin-lzyyd.ondigitalocean.app/climatevisitor/currently-visiting/'



        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }

        explore_response = requests.get(explore_data_endpoint, headers=headers)

        if explore_response.status_code == 200:
            explore_data = explore_response.json()

            current_location_id = explore_data.get('explore_location')

            if not current_location_id:
                # Don't actually need to pass in id, there will only ever be one current twin location
                current_location_id = explore_data.get('twin_location')

                if not current_location_id:
                    return None

                current_location_data = requests.get(twin_endpoint, headers=headers)
                return current_location_data.json()
            
            discovery_location_endpoint = f'{discovery_locations_endpoint}{current_location_id}/'
            current_location_data = requests.get(discovery_location_endpoint, headers=headers)
            return current_location_data.json()
            
          

        twin_response = requests.get(twin_endpoint, headers=headers)

        if twin_response.status_code == 200:
            return twin_response.json()
        
        else:
            # logger.error(f"Error: {twin_response.status_code}")
            return None
            

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        # logger.info("WebSocket connection closed")

    def update_location(self, event):
        # logger.debug(f"Received update_locations event: {event}")
        if event is None:
            self.send(text_data=json.dumps({
                'name': "You are home",
            }))
        elif 'latitude' in event and 'longitude' in event:
            self.send(text_data=json.dumps({
                'name': event['name'],
                'latitude': event['latitude'],
                'longitude': event['longitude'],
            }))

     
        # logger.info(f"Received location update: Location - {event['name']}, Latitude - {event['latitude']}, Longitude - {event['longitude']}")

    '''
    def current_location(self, event):
        logger.debug(f"Received update_location event from Celery: {event}")
        self.send(text_data=json.dumps({
            'type': 'current_location',
            'name': f"! Scheduled Task Test ! {event['name']}",
            'latitude': event['latitude'],
            'longitude': event['longitude'],
        }))
        logger.info("Received location update from Celery")
    '''

    def authenticate_user(self):
        auth = self.scope.get('query_string', b'').decode()
        user_token = parse_qs(auth).get('user_token', [None])[0]
        if user_token:
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                access_token = AccessToken(user_token)
                user = self.get_user(access_token)
                return user, access_token
            except:
                # WARNING: This is returning other token
                return self.get_demo_user() 
        else:
            # WARNING: This is returning other token
            return self.get_demo_user() 

    def get_user(self, access_token):
        try:
            user_id = access_token['user_id']
            user = self.get_user_model().objects.get(id=user_id)
            return user, access_token
        except:
            return None, None

    def get_demo_user(self):


        try:
            demo_user = self.get_user_model().objects.get(username='sara')

            from rest_framework_simplejwt.tokens import AccessToken
            demo_token = AccessToken.for_user(demo_user)
            
            logger.debug(f"LocationUpdateConsumer generated token: {demo_token}")

            # Need to conform to one token eventually, but this will work for demo purposes
            endpoint_demo_token = "f38e6b71380f11f62071126b0ff43fc0a2689982"  
            
            return demo_user, endpoint_demo_token
        
        except self.get_user_model().DoesNotExist:
            # logger.error("Demo user 'sara' does not exist.")
                
            # Raise an error
            raise Exception("Demo user 'sara' does not exist.")

    @staticmethod
    def get_user_model():
        return apps.get_model('users', 'BadRainbowzUser')
