from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from climatevisitor.tasks.tasks import send_location_update_to_celery

from channels.db import database_sync_to_async
from datetime import datetime
from django.apps import apps
from django.core.cache import cache
import asyncio

from climatevisitor.send_utils import process_location_update

 

import json
import logging

from urllib.parse import parse_qs


EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"



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

    # last_message = None 
    last_notification = None
    current_location_cache = None

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

        # self.send_push_notification(self.user.id, "Push notification", "Test notif!")


        self.accept()
        logger.info("FOCUS HEEEEEERE Location Update WebSocket connection established")

        # self.send_message_from_cache()
        self.send_notif_from_cache()
        self.send_search_progress_from_cache()
        self.send_current_location_from_cache_or_endpoint()


# if there is a location ID in cache, sends this, otherwise checks endpoints, if nothing in endpoints,
 
    def send_current_location_from_cache_or_endpoint(self):
        
        current_location_cache = cache.get(f"current_location_{self.user.id}")

        # SEND CACHED DATA if data in cache and if 'location_id' and 'last_accessed' are in data
        if current_location_cache and 'location_id' in current_location_cache and 'last_accessed' in current_location_cache:
           
            logger.info(f"Data in current location cache for {self.user.id}")
            logger.info(f"location id and last accessed time found in current location cache for {self.user.id}")
                
            self.send(text_data=json.dumps({
                'state': current_location_cache.get('state', None),
                'location_id': current_location_cache.get('location_id'),
                'name': current_location_cache.get('name', 'Error getting location name'),  
                'latitude': current_location_cache.get('latitude', None),
                'longitude': current_location_cache.get('longitude', None),
                'last_accessed': current_location_cache.get('last_accessed')
            }))
        elif current_location_cache and 'name' in current_location_cache:

            logger.info(f"Data in current location cache for {self.user.id}")
            logger.info(f"name found in current location cache for {self.user.id}")

            self.send(text_data=json.dumps({
                'location_id': None,
                'state': current_location_cache.get('state', None),
                'name': current_location_cache.get('name', 'Error getting location name'),  
                'latitude': None,
                'longitude': None,
                'last_accessed': None
            }))
                

        
        # REFETCH DATA FROM ENDPOINT and save new cache if no cache, or if 'location_id' and 'last_accessed' are not in cache
        else:
            logger.info(f"Either current location data does not exist, or it does not contain 'location_id' and/or 'last_accessed' keys for {self.user.id}, getting data from endpoint")
            
            twin_location_type, explore_location_type = self.fetch_data_from_endpoint(self.token) # will return 1 of 3 combos: location none, none location, or none none 
            if twin_location_type:
                logger.info(f"Sending current location twin type data for {self.user.id}")
                self.update_location(twin_location_type)
            elif explore_location_type:
                logger.info(f"Sending current location explore type data for {self.user.id}")
                self.update_location(explore_location_type)
            else:
                # SEND EMPTY UPDATE if endpoint has no twin or explore location
                logger.info(f"Explore endpoint returned no current location, sending empty event to location update for {self.user.id}")
                 
                self.update_location(self.create_empty_location_update())


    # def send_message_from_cache(self):
    #     last_message = cache.get(f"last_message_{self.user.id}")
    #     if last_message:
    #         logger.info(f"Sending last_message to user {self.user.id}: {last_message}")
    #         self.send(text_data=json.dumps({'message': last_message}))
    #     else:
    #         logger.info("No message in cache for this user")


    def send_notif_from_cache(self):
        last_notification = cache.get(f"last_notification_{self.user.id}")
        if last_notification:
            logger.info(f"Sending last_notification to user {self.user.id}: {last_notification}")
            self.send(text_data=json.dumps({'notification': last_notification}))
        else:
            logger.info("No notification in cache for this user")


    
    def send_search_progress_from_cache(self):
        last_search_progress = cache.get(f"last_search_progress_{self.user.id}")
        if last_search_progress:
            logger.info(f"Sending last_search_progress to user {self.user.id}: {last_search_progress}")
            self.send(text_data=json.dumps({'search_progress': last_search_progress}))
        else:
            logger.info("No search progress in cache for this user")
 

    def create_empty_location_update(self):
        empty_update = {
            'state': 'home',
            'location_id': None,
            'name': 'You are home', 
            'latitude': None,
            'longitude': None,
            'last_accessed': None,
        }
        return empty_update


 


    # def send_message_event(self, event):
    #     """Handles sending a 'message' event and stores it in cache."""
    #     if not self.user:
    #         logger.error("No user found when trying to send message event.")
    #         return
        
    #     message_data = event.get("message")
    #     if message_data:
    #         logger.debug(f"Saving last_message for user {self.user.id}: {message_data}")
    #         cache.set(f"last_message_{self.user.id}", message_data) # no timeout , timeout=86400)  # Store for 1 day
    #         self.send(text_data=json.dumps({'message': message_data}))


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

               # self.send_message_from_cache()
                self.send_notif_from_cache()
                self.send_search_progress_from_cache()
                self.send_current_location_from_cache_or_endpoint()

                user_id = self.user.id
                self.send_push_notification(user_id, 'Manual Notification', 'This is a manually triggered notification!')


   

    def send_push_notification(self, user_id, title, message):
        """
        Function to send a push notification to the user via Expo.
        """
        from django.core.exceptions import ObjectDoesNotExist

        try:
           
            Settings = self.get_user_settings_model() 
            try:
                settings = Settings.objects.get(id=user_id)
                expo_push_token = settings.expo_push_token

                if not expo_push_token:
                    logger.error(f"No Expo push token found for user {user_id}")
                    return
            except ObjectDoesNotExist: 
                logger.error(f"No settings found for user {user_id}")
                return

        except Exception as e:
            logger.error(f"Error sending push notification to user {user_id}: {str(e)}")
            return  
 
        data = {
            "to": expo_push_token,
            "title": title,
            "body": message,
            "priority": "high", 
        }

        # Set headers for the request
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Send the request to Expo Push Notification API
        response = requests.post(EXPO_PUSH_URL, json=data, headers=headers)

        # Check the response from Expo
        if response.status_code == 200:
            logger.info(f"Notification sent successfully to user {user_id}")
        else:
            logger.error(f"Failed to send notification: {response.status_code} - {response.text}")

                    
    def fetch_data_from_endpoint(self, token):
        from rest_framework_simplejwt.tokens import AccessToken

        explore_data_endpoint = 'https://climatetwin.com/climatevisitor/currently-exploring/v2/'
        # explore_data_endpoint = 'http://localhost:8000/climatevisitor/currently-exploring/v2/'
 
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

            #print('EXPLORE ENDPOINT DATA: ', explore_data)

            current_location_visiting_id = (
                explore_data.get('location_visiting_id')
            )

            current_location_expired = (
                explore_data.get('expired')
            )

            current_location_last_accessed = (
                explore_data.get('last_accessed')
            )    

            if current_location_expired or current_location_visiting_id is None or current_location_last_accessed is None:
                return None, None
            
            # already a string
            # last_accessed_str = current_location_last_accessed.isoformat()  
            
            twin_location_id = None  
            explore_location_id = None

            if explore_data.get('explore_location') is not None:
                explore_location_id = explore_data['explore_location'].get('id')

                if explore_location_id and explore_location_id == current_location_visiting_id:
                    explore_dict = explore_data.get('explore_location')

                    # this is formatted for update_location method and should only be fetched 
                    # if there isn't already something in the cache
                    # update_location method will then cache it
                    event_data = {
                        'state': 'exploring',
                        'location_id': current_location_visiting_id,
                        'name': explore_dict.get('name', 'Unknown'),   
                        'latitude': explore_dict.get('latitude', None),  
                        'longitude': explore_dict.get('longitude', None),
                        'last_accessed': current_location_last_accessed, 
                    }
                    return None, event_data
                return None, None

            elif explore_data.get('twin_location') is not None:
                twin_location_id = explore_data['twin_location'].get('id')

                if twin_location_id and twin_location_id == current_location_visiting_id:
                    twin_dict = explore_data.get('twin_location')

                    # this is formatted for update_location method and should only be fetched 
                    # if there isn't already something in the cache
                    # update_location method will then cache it
                    event_data = {
                        'state': 'exploring', # make more accurate later
                        'location_id': current_location_visiting_id,
                        'name': twin_dict.get('name', 'Unknown'),  
                        'latitude': twin_dict.get('latitude', None),  
                        'longitude': twin_dict.get('longitude', None),
                        'last_accessed': current_location_last_accessed, 
                        
                    }
                    return event_data, None
                # Not sure I need all these return statements below or why the top one isn't returning None, None...
                return 
            return None, None
        return None, None 
    
    # setting cache in ClimateTwinFinder in case websocket connection is closed, so that it can be accessed quickly 
    def twin_location_search_progress_update(self, event):
        search_progress_update = event['search_progress']

        # cache_key = f"last_search_progress_{self.user.id}" 
        # cache.set(cache_key, search_progress_update) # no timeout , timeout=86400)

        self.send(text_data=json.dumps({'search_progress': search_progress_update}))


    # REMOVE, BECAUSE I ADDED THE MESSAGES TO THE LOCATION UPDATES INSTEAD
    # def search_for_ruins(self, event): 
    #     #logger.debug(f"Received search_for_ruins event: {event}") # log incoming data
    #     message_data = event['message']
    #     #logger.debug(f"Message data extracted: {message_data}")

    #     cache_key = f"last_message_{self.user.id}" 
    #     cache.set(cache_key, message_data) # no timeout , timeout=86400)
    #     logger.debug(f"search_for_ruins message cached successfully  for user {self.user.id} with key: {cache_key} and timeout 86400")
 
    #     self.send(text_data=json.dumps({'message': message_data}))
    #     logger.debug(f"Sent search_for_ruins message to client: {message_data}")

       
 

    # def explore_locations_ready(self, event):
    #     logger.debug(f"Received update_location event: {event}")

    #     message_data = event['message']
    #     cache.set(f"last_message_{self.user.id}", message_data) # no timeout , timeout=86400)
    #     self.send(text_data=json.dumps({'message': message_data}))




    # def no_ruins_found(self, event):
    #     logger.debug(f"Received update_location event: {event}")

    #     message_data = event['message']
    #     cache.set(f"last_message_{self.user.id}", message_data) # no timeout , timeout=86400)
    #     self.send(text_data=json.dumps({'message': message_data}))


    # def clear_message(self, event):
    #     logger.debug(f"Received update_location event: {event}")

    #     message_data = event['message']
    #     cache.set(f"last_message_{self.user.id}", message_data) # no timeout, timeout=86400)
    #     self.send(text_data=json.dumps({'message': message_data}))


    # def returned_home_message(self, event):

    #     logger.debug(f"Received update_location event: {event}")

    #     message_data = event['message']
    #     cache.set(f"last_message_{self.user.id}", message_data) # no timeout , timeout=86400)
    #     self.send(text_data=json.dumps({'message': message_data})) 

    def gift_notification(self, event):
        logger.debug(f"Received gift_notification event: {event}")

        notification_data = event['notification']
        recipient_id = event['recipient_id']  
        cache.set(f"notification_{recipient_id}", notification_data) # no timeout , timeout=86400)
        self.send(text_data=json.dumps({'notification': notification_data}))


    def friend_notification(self, event):

        logger.debug(f"Received update_location event: {event}")

        notification_data = event['notification']
        recipient_id = event['recipient_id'] 
        cache.set(f"notification_{recipient_id}", notification_data) # no timeout, timeout=86400)
        self.send(text_data=json.dumps({'notification': notification_data}))
   
   
    def disconnect(self, close_code):
        """
        Handles WebSocket disconnection and cleans up the connection.
        """
        if hasattr(self, 'group_name'):  # Was getting error upon app reinitializing that this wasn't defined, so added this check
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name
            )
            logger.info(f"Location update WebSocket disconnected for group {self.group_name}")
        else:
            logger.warning("WebSocket disconnect called, but group_name was never set.")

    def update_with_old_location_on_fail(self):
        """
        Calls fetch from endpoints code to reset location in the event a new one can't be saved.
        """
        self.send_current_location_from_cache_or_endpoint()


    # def update_location(self, event):
    #     """
    #     Sends location updates to the client.
    #     """
    #     logger.debug(f"Received update_locations event: {event}")
    #     if event is None:
    #         # self.send(text_data=json.dumps({'name': "You are home"}))
    #         self.send(text_data=json.dumps({
    #             'state': 'home',
    #             'location_id' : None,
    #             'name': "You are home",
    #             'latitude': None,
    #             'longitude': None,
    #             'last_accessed': None,
    #         }))

    #         self.send_push_notification(self.user.id, "ClimateTwin location update", "You are home")

    # # elif 'latitude' in event and 'longitude' in event:
    #     else:

            
    #         self.send(text_data=json.dumps({
    #             'state': event.get('state', 'home'),
    #             'location_id': event.get('location_id', None), 
    #             'name': event.get('name', 'Error'),  
    #             'latitude': event.get('latitude', None),  
    #             'longitude': event.get('longitude', None), 
    #             'last_accessed': event.get('last_accessed', None), 
    #         }))

    #         location_name = event.get('name', 'Error') # repeat of above

    #         self.send_push_notification(self.user.id, "ClimateTwin location update", f"{location_name}")

    #     cache_key = f"current_location_{self.user.id}"
    #     logger.debug(f"Caching current location for user {self.user.id} with key: {cache_key}")
 
    #     location_data = {
    #         'location_id': event.get('location_id', None),
    #         'state': event.get('state', None),
    #         'name': event.get('name', 'Error'),
    #         'latitude': event.get('latitude', None),
    #         'longitude': event.get('longitude', None),
    #         'last_accessed': event.get('last_accessed', None),
    #     }
 
    #     cache.set(cache_key, location_data)  # no timeout, always store last location update
    def update_location(self, event):
        """
        Sends location updates to the client.
        """
        logger.debug(f"Received update_locations event: {event}")

        user_id = self.user.id

        if event is None:
            self.send(text_data=json.dumps({
                'state': 'home',
                'location_id': None,
                'name': "You are home",
                'latitude': None,
                'longitude': None,
                'last_accessed': None,
            }))

            # Still call the utility function to handle cache + push
            process_location_update(
                user_id=user_id,
                state='home',
                location_id=None,
                name="You are home",
                latitude=None,
                longitude=None,
                last_accessed=None,
            )
        else:
            self.send(text_data=json.dumps({
                'state': event.get('state', 'home'),
                'location_id': event.get('location_id', None),
                'name': event.get('name', 'Error'),
                'latitude': event.get('latitude', None),
                'longitude': event.get('longitude', None),
                'last_accessed': event.get('last_accessed', None),
            }))

            # Use utility function to handle caching and push
            process_location_update(
                user_id=user_id,
                state=event.get('state', 'home'),
                location_id=event.get('location_id', None),
                name=event.get('name', 'Error'),
                latitude=event.get('latitude', None),
                longitude=event.get('longitude', None),
                last_accessed=event.get('last_accessed', None),
            )


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
    
    @staticmethod
    def get_user_settings_model():
        return apps.get_model('users', 'UserSettings')




