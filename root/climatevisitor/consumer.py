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
        self.user = self.authenticate_user()

        if self.user:
            self.group_name = f'climate_updates_{self.user.id}'
            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            ) 
            self.accept()
            self.send(text_data=json.dumps({
                'message': f"User retrieved: {self.user}"
            }))
        else:
            self.accept()
            self.send(text_data=json.dumps({
                'error': "Authentication failed. Connection closing."
            }))
            self.close()


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
        # Get the query string from the WebSocket connection
        auth = self.scope.get('query_string', b'').decode()
        
        user_token = parse_qs(auth).get('user_token', [None])[0]

        if not user_token:
            raise AuthenticationFailed("No token provided")

        if user_token:
            try: # DRF token authentication
                user, _ = self.authenticate_with_drf_token(user_token)
                
                if user is None:
                    raise AuthenticationFailed("Invalid DRF token")
                 
                jwt_token = AccessToken.for_user(user)

                
                return user #jwt_token
            
            except AuthenticationFailed as drf_auth_error:
                print(f"DRF token authentication failed: {drf_auth_error}")

                # Step 3: Attempt JWT authentication directly
                try:
                    jwt_token = AccessToken(user_token)  # Decode the JWT
                    user_id = jwt_token['user_id']  # Extract user ID from the token payload

                    # Fetch the user from your User model
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)

                    return user #jwt_token

                except Exception as jwt_error:
                    print(f"JWT authentication failed: {jwt_error}") 
                    # logger.error(f"Authentication failed: {e}")
                    raise AuthenticationFailed("JWT authentication failed") 
                    # return self.get_demo_user() 
        # else:
        #     print('Could not parse given user token, fetching demo user')
        #     # If no user token is provided, return the demo user
        #     return self.get_demo_user()

    def authenticate_with_drf_token(self, user_token):
        from rest_framework.authentication import TokenAuthentication
        from rest_framework.exceptions import AuthenticationFailed
        """
        Authenticate the user using the DRF Token authentication.
        """
        try:
            # Authenticate using TokenAuthentication
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



# class LocationUpdateConsumer(WebsocketConsumer):

#     def connect(self):


#         self.user, self.token = self.authenticate_user()  
#         if self.user and self.token:
#             channel_id = self.user.id

#             self.group_name = f'location_update_{channel_id}'

        
#             async_to_sync(self.channel_layer.group_add)(
#                 self.group_name,
#                 self.channel_name
#             ) 
#             self.accept()
#             logger.info("FOCUS HERE Location Update WebSocket connection established")

#             data = self.fetch_data_from_endpoint(self.token)
            
#             self.update_location(data)

#         else:
#             self.accept()
#             self.send(text_data=json.dumps({
#                 'error': "Authentication in LocationUpdateConsumer failed. Connection closing."
#             }))
#             self.close()
         


#     def fetch_data_from_endpoint(self, token):
#         from rest_framework_simplejwt.tokens import AccessToken
#         # Fetch data from endpoint(s)

#         # local
#         # explore_data_endpoint = 'http://localhost:8000/climatevisitor/currently-exploring/'
#         # discovery_locations_endpoint = 'http://localhost:8000/climatevisitor/locations/nearby/'
#         # twin_endpoint = 'http://localhost:8000/climatevisitor/currently-visiting/'
     
#         explore_data_endpoint = 'https://climatetwin.com/climatevisitor/currently-exploring/'
#         discovery_locations_endpoint = 'https://climatetwin.com/climatevisitor/locations/nearby/'
#         twin_endpoint = 'https://climatetwin.com/climatevisitor/currently-visiting/'


#        # Convert token to a string if it's an AccessToken object
#         token_str = str(token) if isinstance(token, AccessToken) else token
     
#         if len(token_str.split('.')) == 3: 
#             auth_header = f'Bearer {token_str}'
#         else: 
#             auth_header = f'Token {token_str}'
        
#         headers = {
#             'Authorization': auth_header,
#             'Content-Type': 'application/json'
#         }
#         explore_response = requests.get(explore_data_endpoint, headers=headers)

#         if explore_response.status_code == 200:
#             explore_data = explore_response.json()

#             current_location_id = explore_data.get('explore_location')

#             if not current_location_id:
#                 # Don't actually need to pass in id, there will only ever be one current twin location
#                 current_location_id = explore_data.get('twin_location')

#                 if not current_location_id:
#                     return None

#                 current_location_data = requests.get(twin_endpoint, headers=headers)
#                 return current_location_data.json()
            
#             discovery_location_endpoint = f'{discovery_locations_endpoint}{current_location_id}/'
#             current_location_data = requests.get(discovery_location_endpoint, headers=headers)
#             return current_location_data.json()
            
          

#         twin_response = requests.get(twin_endpoint, headers=headers)

#         if twin_response.status_code == 200:
#             return twin_response.json()
        
#         else:
#             # logger.error(f"Error: {twin_response.status_code}")
#             return None
            

#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)(
#             self.group_name,
#             self.channel_name
#         )
#         logger.info("update_locations connection closed")

#     def update_location(self, event):
#         logger.debug(f"Received update_locations event: {event}")
#         if event is None:
#             self.send(text_data=json.dumps({
#                 'name': "You are home",
#             }))
#         elif 'latitude' in event and 'longitude' in event:
#             self.send(text_data=json.dumps({
#                 'name': event['name'],
#                 'latitude': event['latitude'],
#                 'longitude': event['longitude'],
#             }))

      

#     def authenticate_user(self):

#         from rest_framework_simplejwt.tokens import AccessToken
#         from rest_framework.exceptions import AuthenticationFailed
#         # Get the query string from the WebSocket connection
#         auth = self.scope.get('query_string', b'').decode()
#         user_token = parse_qs(auth).get('user_token', [None])[0]

#         if not user_token:
#             raise AuthenticationFailed("No token provided")

#         if user_token:
#             try: # DRF token authentication
#                 user, _ = self.authenticate_with_drf_token(user_token)
                
#                 if user is None:
#                     raise AuthenticationFailed("Invalid DRF token")
                
#                 jwt_token = AccessToken.for_user(user)

              
#                 return user, user_token
            
#             except AuthenticationFailed as drf_auth_error:
#                 print(f"DRF token authentication failed: {drf_auth_error}")
 
#                 try:
#                     jwt_token = AccessToken(user_token)   

#                     user_id = jwt_token['user_id']   
#                     from django.contrib.auth import get_user_model
#                     User = get_user_model()
#                     user = User.objects.get(id=user_id)

#                     return user, jwt_token

#                 except Exception as jwt_error:
#                     print(f"JWT authentication failed: {jwt_error}")  
#                     raise AuthenticationFailed("JWT authentication failed") 
  

#     def authenticate_with_drf_token(self, user_token):
#         """
#         Authenticate the user using the DRF Token authentication.
#         """
#         from rest_framework.authentication import TokenAuthentication
#         from rest_framework.exceptions import AuthenticationFailed
#         try:
#             # Authenticate using TokenAuthentication
#             auth = TokenAuthentication()
#             user, token = auth.authenticate_credentials(user_token)
#             return user, token
#         except AuthenticationFailed:
#             return None, None

#     def get_user(self, access_token):
#         try:
#             user_id = access_token['user_id']
#             user = self.get_user_model().objects.get(id=user_id)
#             return user, access_token
#         except:
#             return None, None
 

#     @staticmethod
#     def get_user_model():
#         return apps.get_model('users', 'BadRainbowzUser')
    



class LocationUpdateConsumer(WebsocketConsumer):

    def connect(self):
        self.user, self.token = self.authenticate_user()
        self.connected = False  # Ensures proper handling of connection state

        if self.user and self.token:
            channel_id = self.user.id
            self.group_name = f'location_update_{channel_id}'

            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )
            self.accept()
            self.connected = True
            logger.info("FOCUS HERE Location Update WebSocket connection established")

            data = self.fetch_data_from_endpoint(self.token)
            self.update_location(data)
        else:
            self.accept()
            self.send(text_data=json.dumps({
                'error': "Authentication in LocationUpdateConsumer failed. Connection closing."
            }))
            self.close()
            return

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

        explore_data_endpoint = 'https://climatetwin.com/climatevisitor/currently-exploring/'
        discovery_locations_endpoint = 'https://climatetwin.com/climatevisitor/locations/nearby/'
        twin_endpoint = 'https://climatetwin.com/climatevisitor/currently-visiting/'

        #         explore_data_endpoint = 'http://localhost:8000/climatevisitor/currently-exploring/'
    #         discovery_locations_endpoint = 'http://localhost:8000/climatevisitor/locations/nearby/'
    #         twin_endpoint = 'http://localhost:8000/climatevisitor/currently-visiting/'
        

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
        twin_response = requests.get(twin_endpoint, headers=headers)

        if twin_response.status_code == 200:
            return twin_response.json()
        
        return None  # If nothing found

    def explore_locations_ready(self, event):
        # logger.debug(f"Received update_coordinates event: {event}")
        self.send(text_data=json.dumps({
            'message': event['message'], 
        }))


    def send_no_ruins_found(self, event):
        # logger.debug(f"Received update_coordinates event: {event}")
        self.send(text_data=json.dumps({
            'message': event['message'], 
        }))

    def disconnect(self, close_code):
        """
        Handles WebSocket disconnection and cleans up the connection.
        """
        self.connected = False
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
            raise AuthenticationFailed("No token provided")

        try:
            user, _ = self.authenticate_with_drf_token(user_token)
            if user is None:
                raise AuthenticationFailed("Invalid DRF token")
            return user, user_token
        except AuthenticationFailed:
            try:
                jwt_token = AccessToken(user_token)
                user_id = jwt_token['user_id']
                User = self.get_user_model()
                user = User.objects.get(id=user_id)
                return user, jwt_token
            except Exception as e:
                logger.error(f"JWT authentication failed: {e}")
                raise AuthenticationFailed("JWT authentication failed")

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




# class LocationUpdateConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         """
#         Handles WebSocket connection, authenticates the user, and fetches initial location data.
#         """
#         self.user, self.token = await self.authenticate_user()
#         self.connected = False  # Track connection state

#         if self.user and self.token:
#             channel_id = self.user.id
#             self.group_name = f'location_update_{channel_id}'

#             await self.channel_layer.group_add(self.group_name, self.channel_name)
#             await self.accept()
#             self.connected = True
#             logger.info("Location Update WebSocket connection established")

#             # Fetch and send initial location data
#             data = await self.fetch_data_from_endpoint(self.token)
#             await self.update_location(data)
#         else:
#             await self.accept()
#             await self.send(text_data=json.dumps({'error': "Authentication failed. Connection closing."}))
#             await self.close()

#     async def receive(self, text_data=None, bytes_data=None):
#         """
#         Keeps the connection alive and listens for incoming messages from the client.
#         """
#         if text_data:
#             logger.debug(f"Received WebSocket message: {text_data}")
#             message = json.loads(text_data)
            
#             # Handle incoming messages (e.g., refresh location data)
#             if message.get("action") == "refresh":
#                 data = await self.fetch_data_from_endpoint(self.token)
#                 await self.update_location(data)

#     async def fetch_data_from_endpoint(self, token):
#         """
#         Fetches data asynchronously from external API endpoints.
#         """
#         from rest_framework_simplejwt.tokens import AccessToken

#         # explore_data_endpoint = 'https://climatetwin.com/climatevisitor/currently-exploring/'
#         # discovery_locations_endpoint = 'https://climatetwin.com/climatevisitor/locations/nearby/'
#         # twin_endpoint = 'https://climatetwin.com/climatevisitor/currently-visiting/'

#         explore_data_endpoint = 'http://localhost:8000/climatevisitor/currently-exploring/'
#         discovery_locations_endpoint = 'http://localhost:8000/climatevisitor/locations/nearby/'
#         twin_endpoint = 'http://localhost:8000/climatevisitor/currently-visiting/'
     
#         token_str = str(token) if isinstance(token, AccessToken) else token
#         auth_header = f'Bearer {token_str}' if len(token_str.split('.')) == 3 else f'Token {token_str}'
        
#         headers = {'Authorization': auth_header, 'Content-Type': 'application/json'}

#         async def async_request(url):
#             return await sync_to_async(requests.get)(url, headers=headers)

#         explore_response = await async_request(explore_data_endpoint)

#         if explore_response.status_code == 200:
#             explore_data = explore_response.json()
#             current_location_id = explore_data.get('explore_location') or explore_data.get('twin_location')

#             if not current_location_id:
#                 return None

#             if 'twin_location' in explore_data:
#                 return (await async_request(twin_endpoint)).json()

#             discovery_location_endpoint = f'{discovery_locations_endpoint}{current_location_id}/'
#             return (await async_request(discovery_location_endpoint)).json()

#         twin_response = await async_request(twin_endpoint)
#         return twin_response.json() if twin_response.status_code == 200 else None

#     async def disconnect(self, close_code):
#         """
#         Handles WebSocket disconnection and removes the connection from the group.
#         """
#         self.connected = False
#         await self.channel_layer.group_discard(self.group_name, self.channel_name)
#         logger.info("Location Update WebSocket connection closed")

#     async def update_location(self, event):
#         """
#         Sends location updates to the client.
#         """
#         logger.debug(f"Received update_locations event: {event}")
#         if event is None:
#             await self.send(text_data=json.dumps({'name': "You are home"}))
#         elif 'latitude' in event and 'longitude' in event:
#             await self.send(text_data=json.dumps({
#                 'name': event['name'],
#                 'latitude': event['latitude'],
#                 'longitude': event['longitude'],
#             }))

#     async def authenticate_user(self):
#         """
#         Authenticates the user using either DRF Token or JWT.
#         """
#         from rest_framework_simplejwt.tokens import AccessToken
#         from rest_framework.exceptions import AuthenticationFailed

#         auth = self.scope.get('query_string', b'').decode()
#         user_token = parse_qs(auth).get('user_token', [None])[0]

#         if not user_token:
#             raise AuthenticationFailed("No token provided")

#         try:
#             user, _ = await self.authenticate_with_drf_token(user_token)
#             if user is None:
#                 raise AuthenticationFailed("Invalid DRF token")
#             return user, user_token
#         except AuthenticationFailed:
#             try:
#                 jwt_token = AccessToken(user_token)
#                 user_id = jwt_token['user_id']
#                 User = await self.get_user_model()
#                 user = await sync_to_async(User.objects.get)(id=user_id)
#                 return user, jwt_token
#             except Exception as e:
#                 logger.error(f"JWT authentication failed: {e}")
#                 raise AuthenticationFailed("JWT authentication failed")

#     async def authenticate_with_drf_token(self, user_token):
#         """
#         Authenticates the user using DRF Token authentication.
#         """
#         from rest_framework.authentication import TokenAuthentication
#         from rest_framework.exceptions import AuthenticationFailed

#         try:
#             auth = TokenAuthentication()
#             user, token = await sync_to_async(auth.authenticate_credentials)(user_token)
#             return user, token
#         except AuthenticationFailed:
#             return None, None

#     async def get_user(self, access_token):
#         """
#         Retrieves the user asynchronously from the access token.
#         """
#         try:
#             user_id = access_token['user_id']
#             User = await self.get_user_model()
#             user = await sync_to_async(User.objects.get)(id=user_id)
#             return user, access_token
#         except Exception:
#             return None, None

#     @staticmethod
#     async def get_user_model():
#         """
#         Returns the custom user model asynchronously.
#         """
#         return apps.get_model('users', 'BadRainbowzUser')