from django.conf import settings
import requests


google_api_key = settings.GOOGLE_MAPS_API_KEY
open_map_api_key = settings.OPEN_MAP_API_KEY


def get_street_view_metadata(latitude, longitude):
    base_url = "https://maps.googleapis.com/maps/api/streetview/metadata"

    params = {
        "location": f"{latitude},{longitude}",
        "key": google_api_key,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        metadata = response.json()
        # Check if there is imagery available
        if metadata.get("status") == "OK":
            return True
        else:
            return False
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return False


#loose function for right now

def get_street_view_image(latitude, longitude, size="600x300", heading=None, pitch=None):
    base_url = "https://maps.googleapis.com/maps/api/streetview"

    # Check if Street View imagery is available
    if not get_street_view_metadata(latitude, longitude):
        print("No Street View imagery available at the specified location.")
        return None

    params = {
        "location": f"{latitude},{longitude}",
        "size": size,
        "key": google_api_key,
    }

    if heading is not None:
        params["heading"] = heading
    if pitch is not None:
        params["pitch"] = pitch

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        # Return the street view image URL
        return response.url
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None



import requests
import xml.etree.ElementTree as ET
from math import radians, sin, cos, sqrt, atan2, degrees
from bisect import insort, bisect, bisect_left

from geopy.distance import geodesic

class OpenMapAPI:
    endpoint = "https://overpass-api.de/api/interpreter"

    @staticmethod
    def haversine_distance_first(lat1, lon1, lat2, lon2):
        # Radius of the Earth in miles
        R = 3958.8

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        distance = int(geodesic((lat1, lon1), (lat2, lon2)).miles)

        #return geodesic((lat1, lon1), (lat2, lon2)).miles
        return distance
    

    # testing
    # if this endpoint doesn't work, can use the Google reverse_geocode in ClimateTwinFinder
    # conversely if this does work, consider using this in ClimateTwinFinder 
    @staticmethod
    def reverse_geocode(lat, lon):
        try:
            response = requests.get(
                'https://nominatim.openstreetmap.org/reverse',
                params={
                    'format': 'json',
                    'lat': lat,
                    'lon': lon,
                    'zoom': 10,
                    'addressdetails': 1
                },
                headers={
                    'User-Agent': 'OpenMapAPI/1.0'
                }
            )
            response.raise_for_status()
            data = response.json()
            address = data.get('address', {})
            return {
                'country': address.get('country'),
                'state': address.get('state'),
                'city': address.get('city') or address.get('town') or address.get('village')
            }
        except Exception as e:
            print(f"Reverse geocoding failed for ({lat}, {lon}): {e}")
            return {}

    @staticmethod
    def find_ancient_ruins(latitude, longitude, radius=60000, num_results=8): # radius is in meters, 60000 = 37 miles # radius was prev 100000 meters and in parent, num was 15 and in parent
        overpass_query = f"node(around:{radius},{latitude},{longitude})['historic'='ruins'];out;"

        params = {
            "data": overpass_query
        }

        try:
            response = requests.get(OpenMapAPI.endpoint, params=params)
            response.raise_for_status()  # Raise an error for bad responses (e.g., 404, 500)

            # Check if the response content is not empty
            if response.content:
                # Process XML content using ElementTree
                root = ET.fromstring(response.content)
                nodes = root.findall('.//node')

                # Convert XML data to a list of dictionaries with distance and direction information
                data = []


                for node in nodes:
                    lat = float(node.attrib['lat'])
                    lon = float(node.attrib['lon'])

                    tags = {tag.attrib['k']: tag.attrib['v'] for tag in node.findall('tag')}

                    distance = OpenMapAPI.haversine_distance(lat, lon, latitude, longitude)

                    direction_rad = atan2(lon - longitude, lat - latitude)
                    direction_deg = (degrees(direction_rad) + 360) % 360
                    direction = OpenMapAPI.get_direction_word(direction_deg)

                    # Add reverse geocoded location info
                    location_info = OpenMapAPI.reverse_geocode(lat, lon)
                    # time.sleep(1)  # Respect API rate limits

                    ruin_info = {
                        'id': node.attrib['id'],
                        'lat': lat,
                        'lon': lon,
                        'tags': tags,
                        'distance_miles': distance,
                        'direction_deg': direction_deg,
                        'direction': direction,
                    }

                    ruin_info['country'] = location_info.get('country', None)
                    ruin_info['state'] = location_info.get('state', None)
                    ruin_info['city_name'] = location_info.get('city', None)

                    index_to_insert = bisect_left([entry['distance_miles'] for entry in data], distance)
                    data.insert(index_to_insert, ruin_info)

                    data.sort(key=lambda x: x['distance_miles'])

                    if num_results is not None and len(data) >= num_results:
                        break

                # for node in nodes:
                #     tags = {tag.attrib['k']: tag.attrib['v'] for tag in node.findall('tag')}

                #     # Calculate distance for each ruin
                #     distance = OpenMapAPI.haversine_distance(
                #         float(node.attrib['lat']), float(node.attrib['lon']), latitude, longitude
                #     )

                #     direction_rad = atan2(
                #         float(node.attrib['lon']) - longitude, float(node.attrib['lat']) - latitude
                #     )
                #     direction_deg = (degrees(direction_rad) + 360) % 360

                #     # Convert direction_deg to direction_word
                #     direction = OpenMapAPI.get_direction_word(direction_deg)

                #     index_to_insert = bisect_left([entry['distance_miles'] for entry in data], distance)
                #     data.insert(index_to_insert, {
                #         'id': node.attrib['id'],
                #         'lat': node.attrib['lat'],
                #         'lon': node.attrib['lon'],
                #         'tags': tags,
                #         'distance_miles': distance,
                #         'direction_deg': direction_deg,
                #         'direction': direction  # Add direction word information
                #     })

                #     # Sort the data list based on 'distance_miles'
                #     data.sort(key=lambda x: x['distance_miles'])

                #     # Check if the desired number of results is reached
                #     if num_results is not None and len(data) >= num_results:
                #         break

                print(f"Total discovery locations found: {len(data)}")
                # for entry in data: 
                #     print(f"ID: {entry['id']}, Distance: {entry['distance_miles']} miles")

                return data



        except requests.exceptions.HTTPError as errh:
            print("HTTP Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Error:", err)


    @staticmethod
    def get_direction_word(direction_deg):
        directions = ["North", "Northeast", "East", "Southeast", "South", "Southwest", "West", "Northwest", "North"]
        index = round(direction_deg / 45) % 8
        print(f"Direction (degrees): {direction_deg}")
        print(f"Index: {index}")
        return directions[index]



    @staticmethod
    def get_nearest_ruin(latitude, longitude, radius):
        ruins_data = OpenMapAPI.find_ancient_ruins(latitude, longitude, radius)
        if ruins_data:
            # Return the information of the nearest ruin (first in the sorted list)
            ruins_data = [ruins_data[0]]
            return ruins_data
        else:
            print("No ruins found.")

    @staticmethod
    def print_results(results):
        for ruin in results:
            print(f"Ruins ID: {ruin['id']}")
            print(f"Location: Latitude {ruin['lat']}, Longitude {ruin['lon']}")
            print(f"Distance: {ruin['distance_miles']:.2f} miles")
            print(f"Direction: {ruin.get('direction', 'Unknown')}"),
            print(f"Direction Degree: {ruin['direction_deg']}"),
            print("Tags:")
            for key, value in ruin['tags'].items():
                print(f"  {key}: {value}")
            print("\n" + "="*30 + "\n")


    @staticmethod
    def format_ruins_for_post(results):
        formatted_ruins = {}

        for ruin in results:
            tags = ruin.get('tags', {})
            name = tags.get('name', 'a mystery location')

            formatted_ruin = {
                "direction_deg": ruin['direction_deg'],
                "direction": (ruin.get('direction', 'Unknown')),
                "miles_away": round(ruin['distance_miles']),
                "id": ruin['id'],
                "latitude": ruin['lat'],
                "longitude": (ruin['lon']),
                "tags": tags,
                #"name": name  # Add the name to the formatted_ruin dictionary
            }
            formatted_ruins[name] = formatted_ruin

        return formatted_ruins


#add ons specific to my current usage :)

    @staticmethod
    def compare_wind_to_ruin(wind_direction_deg, ruin_direction_deg, ruin_direction_word):
        ruin_direction_degrees = {
            "North": 0,
            "Northeast": 45,
            "East": 90,
            "Southeast": 135,
            "South": 180,
            "Southwest": 225,
            "West": 270,
            "Northwest": 315
        }

        # Adjust wind direction to account for wind coming from
        adjusted_wind_direction_deg = (wind_direction_deg + 180) % 360

        # Calculate the variance in degrees

        variance_deg = abs(adjusted_wind_direction_deg - ruin_direction_deg)
        closest_direction_word = min(ruin_direction_degrees, key=lambda x: abs(ruin_direction_degrees[x] - variance_deg))


        # Check if the adjusted wind direction is going in the direction of the ruin
        if adjusted_wind_direction_deg - 45 <= ruin_direction_deg <= adjusted_wind_direction_deg + 45:
            return {
                "status": "The wind is going in the same direction as the ruin.",
                "wind_agreement_score": variance_deg,
                "closest_direction_word": ruin_direction_word
            }



        elif adjusted_wind_direction_deg - 180 - 45 <= ruin_direction_deg <= adjusted_wind_direction_deg - 180 + 45:



            return {
                "status": "The wind is going in the opposite direction as the ruin.",
                "wind_agreement_score": variance_deg,
                "closest_direction_word": closest_direction_word
            }
        else:
            # Calculate the variance in degrees
            variance_deg = abs(adjusted_wind_direction_deg - ruin_direction_deg)

            # Find the corresponding direction word for the variance
            closest_direction_word = min(ruin_direction_degrees, key=lambda x: abs(ruin_direction_degrees[x] - variance_deg))

            return {
                "status": f"The wind is not going in the same direction as the ruin.",
                "wind_agreement_score": variance_deg,
                "closest_direction_word": closest_direction_word
            }

    @staticmethod
    def format_ruins_with_wind_compass_for_post(results, wind_direction_deg):
        formatted_ruins = {}

        # Sort results based on 'distance_miles' before processing
        results.sort(key=lambda x: x['distance_miles'])

        for ruin in results:
            tags = ruin.get('tags', {})
            name = tags.get('name', 'a mystery location')

            if not name:
                name = 'a mystery location'

            # Call the compare_wind_to_ruin function to get wind compass information
            wind_compass_info = OpenMapAPI.compare_wind_to_ruin(
                wind_direction_deg, ruin['direction_deg'], ruin.get('direction', 'Unknown')
            )

            # Use the latitude and longitude of the ruin to fetch the street view image
            street_view_image = get_street_view_image(  # Replace with your Google Maps API key
                latitude=ruin['lat'],
                longitude=ruin['lon'],
                size="600x300"  # You can adjust the size as needed
            )

            harmony_check = False

            if (round(wind_compass_info['wind_agreement_score'])) < 45:
                harmony_check = True
            else:
                harmony_check = False

            formatted_ruin = {
                "direction_deg": ruin.get('direction_deg', None),
                "direction": ruin.get('direction', 'Unknown'),
                "miles_away": round(ruin.get('distance_miles', 0)),
                "id": ruin.get('id', None),
                "latitude": ruin.get('lat', None),
                "longitude": ruin.get('lon', None),
                "country": ruin.get('country', None),
                "city_name": ruin.get('city_name', None),
                "state": ruin.get('state', None),
                "tags": tags,
                "wind_compass": wind_compass_info.get('status', None),
                "wind_agreement_score": round(wind_compass_info.get('wind_agreement_score', 0)),
                "wind_harmony": harmony_check
            }

            # formatted_ruin = {
            #     "direction_deg": ruin['direction_deg'],
            #     "direction": ruin.get('direction', 'Unknown'),
            #     "miles_away": round(ruin['distance_miles']),
            #     "id": ruin['id'],
            #     "latitude": ruin['lat'],
            #     "longitude": ruin['lon'],
            #     "country": ruin['country'],
            #     "city_name": ruin['city_name' or None],
            #     # not using state (yet)
            #     "state": (ruin['state']),
            #     "tags": tags,
            #     "wind_compass": (wind_compass_info['status']),
            #     "wind_agreement_score": (round(wind_compass_info['wind_agreement_score'])),
            #     "wind_harmony": harmony_check
            # }

            # Add street view image to the formatted_ruin dictionary if available
            if street_view_image:
                formatted_ruin["street_view_image"] = street_view_image

            formatted_ruins[name] = formatted_ruin

        return formatted_ruins

    @staticmethod
    def print_formatted_ruins_with_wind_compass(formatted_ruins):
        for name, ruin_info in formatted_ruins.items():
            print(f"Ruins Name: {name}")
            print(f"ID: {ruin_info['id']}")
            print(f"Location: Latitude {ruin_info['latitude']}, Longitude {ruin_info['longitude']}")
            print(f"Distance: {ruin_info['miles_away']} miles")
            print(f"Direction: {ruin_info['direction']} ({ruin_info['direction_deg']} degrees)")
            print(f"Wind Compass: {ruin_info['wind_compass']}")
            print(f"Wind Agreement Score: {ruin_info['wind_agreement_score']}")

            # Print street view image URL
            street_view_image_url = ruin_info.get('street_view_image', 'No street view image')
            print(f"Street View Image URL: {street_view_image_url}")

            print("Tags:")
            for key, value in ruin_info['tags'].items():
                print(f"  {key}: {value}")
            print("\n" + "="*30 + "\n")
