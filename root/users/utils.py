# utils.py
import requests
from django.conf import settings

api_key = settings.GOOGLE_MAPS_API_KEY

def get_coordinates(self, address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    self.google_key_count += 1
    data = response.json()

    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location['lat'], location['lng']
    else:
        print(f"Error: Unable to retrieve coordinates for {address}")
        return None