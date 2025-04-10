
  
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


def cache_and_push_notif_location_update(user_id, state, location_id, name, latitude, longitude, last_accessed):
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


# No push
def cache_notif_location_update(user_id, state, location_id, name, latitude, longitude, last_accessed):
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
    # send_push_notification(user_id, "ClimateTwin location update", name)



def cache_and_push_notif_new_gift(user_id, user_username, recipient_id):
    from django.core.cache import cache 

    cache_key = f"last_notification_{recipient_id}"
    new_gift_message = f'{user_username} sent you a treasure!'
    cache.set(cache_key, new_gift_message) #, timeout=3600) 
    send_push_notification(user_id, "ClimateTwin", new_gift_message)


def cache_and_push_notif_accepted_gift(user_id, user_username, recipient_id):
    from django.core.cache import cache 

    cache_key = f"last_notification_{recipient_id}"
    accepted_gift_message = f'{user_username} accepted the treasure you sent them :)'
    cache.set(cache_key, accepted_gift_message) #, timeout=3600) 
    send_push_notification(user_id, "ClimateTwin", accepted_gift_message)
    
    
# I want to test treasures methods above first before implementing these
def cache_and_push_notif_friend_request(user_id, user_username, recipient_id):
    from django.core.cache import cache

    cache_key = f"last_notification_{recipient_id}"
    new_friend_request_message = f'{user_username} has sent you a friend request!'
    cache.set(cache_key, new_friend_request_message) #, timeout=3600) 
    send_push_notification(user_id, "ClimateTwin", new_friend_request_message)
  

def cache_and_push_notif_friend_request_accepted(user_id, user_username, recipient_id):
    from django.core.cache import cache 

    cache_key = f"last_notification_{recipient_id}"
    accepted_friend_request_message = f'{user_username} accepted your friend request :)'
    cache.set(cache_key, accepted_friend_request_message)
    send_push_notification(user_id, "ClimateTwin", accepted_friend_request_message)

  
 # FOR DEBUGGING, using in algorithms_tasks.py
def push_expiration_task_scheduled(user_id, timeout_seconds):
   
    send_push_notification(user_id, 'DEBUGGING', f'Expiration task scheduled to expire location {timeout_seconds} seconds from now.')

 # FOR DEBUGGING, using in algorithms_tasks.py
def push_expiration_task_executed(user_id):
   
    send_push_notification(user_id, 'DEBUGGING', f'Expiration task to expire location has been executed.')


def push_warning_location_expiring_soon(user_id, location_name, minutes_remaining):

    pluralized = 'minutes'

    if minutes_remaining and int(minutes_remaining) <= 1:
        pluralized = 'minute'

    send_push_notification(user_id, f'Heads up!', f'You have {minutes_remaining} {pluralized} left in {location_name}.')


def cache_twin_search_progress(user_id, percentage):
    from django.core.cache import cache 
    cache_key = f"last_search_progress_{user_id}"
    cache.set(cache_key, percentage)


def set_twin_search_lock(user_id, ttl=60*2):
    from django.core.cache import cache 
    lock_key = f"search_active_for_{user_id}"
    cache.set(lock_key, "LOCKED", timeout=ttl)


def check_for_twin_search_lock(user_id):
    from django.core.cache import cache 
    lock_key = f"search_active_for_{user_id}"
    return cache.get(lock_key) is not None


def check_and_set_twin_search_lock(user_id, ttl=60*2):
    from django.core.cache import cache
    lock_key = f"search_active_for_{user_id}"
    return cache.add(lock_key, "LOCKED", timeout=ttl)


def remove_twin_search_lock(user_id):
    from django.core.cache import cache
    lock_key = f"search_active_for_{user_id}"
    cache.delete(lock_key)



