
  
import logging
logger = logging.getLogger(__name__)


import requests

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

 
def get_user_settings_model():
    from django.apps import apps

    return apps.get_model('users', 'UserSettings')


def send_push_notification(user_id, title, message):
    """
    Function to send a push notification to the user via Expo.
    """
    from django.core.exceptions import ObjectDoesNotExist 

    try:
        
        Settings = get_user_settings_model() 
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


def process_location_update(user_id, state, location_id, name, latitude, longitude, last_accessed):
    from django.core.cache import cache 
    
    cache_key = f"current_location_{user_id}"
    location_data = {
        'location_id': location_id,
        'state': state,
        'name': name,
        'latitude': latitude,
        'longitude': longitude,
        'last_accessed': last_accessed,
    }
    cache.set(cache_key, location_data)
    

    send_push_notification(user_id, "ClimateTwin location update", name)
