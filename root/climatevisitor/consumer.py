from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from climatevisitor.tasks.tasks import send_location_update_to_celery

from channels.db import database_sync_to_async
from django.apps import apps
from django.core.cache import cache
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
        self.user = self.authenticate_user()


        if not self.user:
            return
 
        self.group_name = f'climate_updates_{self.user.id}'

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        ) 

        self.accept()
        self.send(text_data=json.dumps({
            'message': f"User retrieved: {self.user}"
        })) 


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        # logger.info("WebSocket connection closed") 
        # logger.info(f"Received coordinates: Country - {event['country_name']}, Temperature - {event['temperature']}, Latitude - {event['latitude']}, Longitude - {event['longitude']}")


        

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

        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework.exceptions import AuthenticationFailed 

        auth = self.scope.get('query_string', b'').decode()
        user_token = parse_qs(auth).get('user_token', [None])[0]

        if not user_token:
            print("No token provided to ClimateTwinConsumer")
            self.close(code=4001)  
            return None 

        try:
            jwt_token = AccessToken(user_token)
            user_id = jwt_token['user_id']
            User = self.get_user_model()
            user = User.objects.get(id=user_id)
            return user #jwt_token

        except Exception as jwt_error:
            print(f"JWT authentication failed: {jwt_error}")

            try:
                user, _ = self.authenticate_with_drf_token(user_token)
                if user is None:
                    raise AuthenticationFailed("Invalid DRF token")
                return user #user_token
            except AuthenticationFailed:
                self.close(code=4001)  # Close WebSocket on auth failure
                return None 


   
               

    def authenticate_with_drf_token(self, user_token):
        from rest_framework.authentication import TokenAuthentication
        from rest_framework.exceptions import AuthenticationFailed
        """
        Authenticate the user using the DRF Token authentication.
        """
        try: 
            auth = TokenAuthentication()
            user, token = auth.authenticate_credentials(user_token)
            return user, token
        except AuthenticationFailed:
            return None, None

    def get_user(self, access_token):
        try:
            user_id = access_token['user_id']
            user = self.get_user_model().objects.get(id=user_id)
            return user, access_token
        except:
            return None, None
  

    @staticmethod
    def get_user_model():
        return apps.get_model('users', 'BadRainbowzUser')




class LocationUpdateConsumer(WebsocketConsumer):

    last_message = None 

    def connect(self):
        self.user, self.token = self.authenticate_user()

        if not self.user or not self.token:
            # If authentication failed, WebSocket is already closed inside authenticate_user()
            return

        channel_id = self.user.id
        self.group_name = f'location_update_{channel_id}'

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()
        logger.info("FOCUS HEEEEEERE Location Update WebSocket connection established")

        data = self.fetch_data_from_endpoint(self.token)
        self.update_location(data)

        last_message = cache.get(f"last_message_{self.user.id}")
        if last_message:
            logger.info(f"Sending last_message to user {self.user.id}: {last_message}")
            self.send(text_data=json.dumps({'message': last_message}))
        else:
               logger.info("No message in cache for this user")

    def send_message_event(self, event):
        """Handles sending a 'message' event and stores it in cache."""
        if not self.user:
            logger.error("No user found when trying to send message event.")
            return
        
        message_data = event.get("message")
        if message_data:
            logger.debug(f"Saving last_message for user {self.user.id}: {message_data}")
            cache.set(f"last_message_{self.user.id}", message_data, timeout=86400)  # Store for 1 day
            self.send(text_data=json.dumps({'message': message_data}))


    def receive(self, text_data=None, bytes_data=None):
        """
        Keeps the connection alive and listens for incoming messages.
        Can be expanded to handle specific commands from the client.
        """
        if text_data:
            logger.debug(f"Received WebSocket message: {text_data}")
            message = json.loads(text_data)
            
            # Handle incoming messages (optional, modify as needed)
            if message.get("action") == "refresh":
                data = self.fetch_data_from_endpoint(self.token)
                self.update_location(data)
                
                    
    def fetch_data_from_endpoint(self, token):
        from rest_framework_simplejwt.tokens import AccessToken

        explore_data_endpoint = 'https://climatetwin.com/climatevisitor/currently-exploring/v2/'
        discovery_locations_endpoint = 'https://climatetwin.com/climatevisitor/locations/nearby/'
        twin_endpoint = 'https://climatetwin.com/climatevisitor/currently-visiting/'

        # explore_data_endpoint = 'http://localhost:8000/climatevisitor/currently-exploring/v2/'
        # discovery_locations_endpoint = 'http://localhost:8000/climatevisitor/locations/nearby/'
        # twin_endpoint = 'http://localhost:8000/climatevisitor/currently-visiting/'
    

        token_str = str(token) if isinstance(token, AccessToken) else token

        if len(token_str.split('.')) == 3:
            auth_header = f'Bearer {token_str}'
        else:
            auth_header = f'Token {token_str}'
        
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }

        explore_response = requests.get(explore_data_endpoint, headers=headers)

        if explore_response.status_code == 200:
            explore_data = explore_response.json()

            # Extract ID from nested objects
            current_location_id = (
                (explore_data.get('explore_location') or {}).get('id') or
                (explore_data.get('twin_location') or {}).get('id')
            )

            if not current_location_id:
                return None

            # If it's a twin location, fetch data from twin endpoint
            if explore_data.get('twin_location'):
                current_location_data = requests.get(twin_endpoint, headers=headers)
                return current_location_data.json()

            # If it's an explore location, fetch from discovery locations
            discovery_location_endpoint = f'{discovery_locations_endpoint}{current_location_id}/'
            current_location_data = requests.get(discovery_location_endpoint, headers=headers)
            return current_location_data.json()

        # If no explore location, check twin location
        # twin_response = requests.get(explore_data_endpoint, headers=headers)

        # if twin_response.status_code == 200:
        #     return twin_response.json()
        
        return None  # If nothing found

    def search_for_ruins(self, event):
        logger.debug(f"Received update_coordinates event: {event}")

        message_data = event['message']
        cache.set(f"last_message_{self.user.id}", message_data, timeout=86400)
        self.send(text_data=json.dumps({'message': message_data}))

        # self.send(text_data=json.dumps({
        #     'message': event['message'], 
        # }))

    def explore_locations_ready(self, event):
        logger.debug(f"Received update_coordinates event: {event}")

        message_data = event['message']
        cache.set(f"last_message_{self.user.id}", message_data, timeout=86400)
        self.send(text_data=json.dumps({'message': message_data}))

        # self.send(text_data=json.dumps({
        #     'message': event['message'], 
        # }))



    def no_ruins_found(self, event):
        logger.debug(f"Received update_coordinates event: {event}")

        message_data = event['message']
        cache.set(f"last_message_{self.user.id}", message_data, timeout=86400)
        self.send(text_data=json.dumps({'message': message_data}))

        # self.send(text_data=json.dumps({
        #     'message': event['message'], 
        # }))


    def clear_message(self, event):
        logger.debug(f"Received update_coordinates event: {event}")

        message_data = event['message']
        cache.set(f"last_message_{self.user.id}", message_data, timeout=86400)
        self.send(text_data=json.dumps({'message': message_data}))
        # self.send(text_data=json.dumps({
        #     'message': event['message'], 
        # }))

    def returned_home_message(self, event):

        logger.debug(f"Received update_coordinates event: {event}")

        message_data = event['message']
        cache.set(f"last_message_{self.user.id}", message_data, timeout=86400)
        self.send(text_data=json.dumps({'message': message_data}))
        # self.send(text_data=json.dumps({
        #     'message': event['message'], 
        # }))

    def disconnect(self, close_code):
        """
        Handles WebSocket disconnection and cleans up the connection.
        """
        #self.connected = False
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        logger.info("update_locations connection closed")

    def update_location(self, event):
        """
        Sends location updates to the client.
        """
        logger.debug(f"Received update_locations event: {event}")
        if event is None:
            self.send(text_data=json.dumps({'name': "You are home"}))
        elif 'latitude' in event and 'longitude' in event:
            self.send(text_data=json.dumps({
                'name': event['name'],
                'latitude': event['latitude'],
                'longitude': event['longitude'],
            }))

    def authenticate_user(self):
        """
        Authenticates the user using either DRF token or JWT.
        """
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework.exceptions import AuthenticationFailed

        auth = self.scope.get('query_string', b'').decode()
        user_token = parse_qs(auth).get('user_token', [None])[0]

        if not user_token:
            print("No token provided")
            self.close(code=4001)  # Custom WebSocket close code for auth failure
            return None, None

        try:
            jwt_token = AccessToken(user_token)
            user_id = jwt_token['user_id']
            User = self.get_user_model()
            user = User.objects.get(id=user_id)
            return user, jwt_token

        except Exception as jwt_error:
            print(f"JWT authentication failed: {jwt_error}")


            try:
                user, _ = self.authenticate_with_drf_token(user_token)
                if user is None:
                    raise AuthenticationFailed("Invalid DRF token")
                return user, user_token
            except AuthenticationFailed:
                self.close(code=4001)  # Close WebSocket on auth failure
                return None, None


    def authenticate_with_drf_token(self, user_token):
        """
        Authenticates the user using DRF Token authentication.
        """
        from rest_framework.authentication import TokenAuthentication
        from rest_framework.exceptions import AuthenticationFailed

        try:
            auth = TokenAuthentication()
            user, token = auth.authenticate_credentials(user_token)
            return user, token
        except AuthenticationFailed:
            return None, None

    def get_user(self, access_token):
        """
        Retrieves the user from the access token.
        """
        try:
            user_id = access_token['user_id']
            user = self.get_user_model().objects.get(id=user_id)
            return user, access_token
        except Exception:
            return None, None

    @staticmethod
    def get_user_model():
        """
        Returns the custom user model.
        """
        return apps.get_model('users', 'BadRainbowzUser')



