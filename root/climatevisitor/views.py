from . import models
from . import serializers
from users.serializers import BadRainbowzUserSerializer
from celery import shared_task, current_app
from celery.result import AsyncResult
from .climatetwinclasses.ClimateEncounterClass import ClimateEncounter
from .climatetwinclasses.ClimateObjectClass import ClimateObject
from .climatetwinclasses.ClimateTwinFinderClass import ClimateTwinFinder
from climatevisitor.send_utils import check_and_set_twin_search_lock, remove_twin_search_lock, push_expiration_task_scheduled
from climatevisitor.profile_funcs import log_view_time, TimedAPIView


from .tasks.algorithms_task import process_climate_twin_request, schedule_expiration_task, process_immediate_expiration_task
from .tasks.tasks import send_location_update_to_celery, send_home_location_update_to_celery, extra_coverage_cache_location_update, send_is_pending_location_update_to_celery
# send_is_pending_location_update_to_celery is in process_climate_twin_request
from .climatetwinclasses.OpenMapAPIClass import OpenMapAPI
from asgiref.sync import sync_to_async

# for last_accessed object serialization in CreateOrUpdateCurrentLocation, to send data to socket
from datetime import datetime

from django.core.cache import cache
from django.shortcuts import render
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema

from drf_yasg import openapi
import json
from rest_framework import generics, status, throttling
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, parser_classes, throttle_classes, permission_classes, schema
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from users.models import Treasure, TreasureOwnerChangeRecord


# Create your views here.
@swagger_auto_schema(operation_id='index')
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def index(request):
    return render(request, 'index.html', {})


@swagger_auto_schema(operation_id='endpoints')
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def endpoints(request):
    return render(request, 'endpoints.html', {})



@swagger_auto_schema(operation_id='demo')
#@throttle_classes([AnonRateThrottle, UserRateThrottle])
def demo(request):
    return render(request, 'demo.html', {})



def acquire_user_lock(user_id, ttl=60*5): # resets in five mins if not unlocked within process_climate_twin_request
    lock_key = f"search_active_for_{user_id}"
    return cache.add(lock_key, "LOCKED", timeout=ttl)

def is_user_locked(user_id):
    lock_key = f"search_active_for_{user_id}"
    return cache.get(lock_key) is not None


def set_user_lock(user_id, ttl=60*5):
    lock_key = f"search_active_for_{user_id}"
    cache.set(lock_key, "LOCKED", timeout=ttl)




@swagger_auto_schema(method='post', order=1, operation_id='createGo', operation_dscription="Main feature of app", request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'address': openapi.Schema(type=openapi.TYPE_STRING, description="User's current address. Must be a valid address.")
        },
        required=['address'],
    ))
@api_view(['POST'])
#@throttle_classes([AnonRateThrottle, UserRateThrottle])
@authentication_classes([TokenAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def go(request):
    """
    Returns a randomized matching climate location and nearby historical sites and pictures if any. 
    
    Uses a utils package that uses Google Map API, Open Street Map, geopandas, math and numpy.

    **How the search logic works**: validates user address and if valid, gets address weather data. Picks a random country and generates 
    a list of coordinates inside that country to compare user weather data against. Loops through this list looking for weather 
    data that meets a specific criteria and makes a new list of candidate locations, keeping track of high variances; if too many high 
    variances, the loop will break and the function to select a random country will get called again. If not enough candidate locations are
    found by the end of the loop, the function to select a random country will also get called again. When enough candidate locations are found,
    this candidate list is looped through (O(1)) to find the closest matching location. (If this selection is missing certain
    data, then the search will begin again from the beginning. I've mostly prevented uninhabited/ocean coordinates from getting
    returned by the time the algorithm gets to this stage, but a few still seem to slip through the cracks.)
    
    From here, weather and wind interactions between home and twin location are calculated, then nearby historical locations within
    a hardcoded radius are found. The results are returned.
    
    **Note**: Makes two Google Maps calls per POST. User limit of two POSTs per day.

    """

    if request.method == 'POST':
        user = request.user
        user_address = request.data.get('address', None)

        if not user_address:
            return Response({'error': 'Address is required'}, status=status.HTTP_400_BAD_REQUEST)

        if user and not (user.is_staff or user.is_superuser): 
            today = timezone.now().date()
            daily_count = models.ClimateTwinLocation.objects.filter(user=user, created_on__date=today).count()
            if daily_count >= 5:
                return Response({'error': 'You have reached the daily limit of visits.'}, status=status.HTTP_400_BAD_REQUEST)

        if not check_and_set_twin_search_lock(user.id):
            return Response({'error': 'A search is already running for your account.'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS)
        
   
         
        process_climate_twin_request.apply_async(args=[user.id, user_address])

        return Response({'detail': 'Search initiated!'}, status=status.HTTP_200_OK)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    '''
    if request.method == 'POST':
        user = request.user
        user_address = request.data.get('address', None)

        if not user_address:
            return Response({'error': 'Address is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user has hit daily limit
        if user and not (user.is_staff or user.is_superuser): 
            today = timezone.now().date()
            daily_count = models.ClimateTwinDiscoveryLocation.objects.filter(user=user, created_on__date=today).count()
            if daily_count >= 3:
                return Response({'error': 'You have reached the daily limit of visits.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create 
        climate_places = ClimateTwinFinder(user_address)

       

        if climate_places.home_climate:
            
            address = list(climate_places.home_climate.keys())[0]
            home_data = climate_places.home_climate[address]
            home_data["name"] = address
            home_data["user"] = request.user.id

            home_location_serializer = serializers.HomeLocationSerializer(data=home_data)
            if home_location_serializer.is_valid():
                home_location_instance = home_location_serializer.save()
            else:
                home_location_instance = None
                print("Error:", home_location_serializer.errors)


        if climate_places.climate_twin:
            home_weather_profile = ClimateObject(climate_places.home_climate)
            climate_twin_weather_profile = ClimateObject(climate_places.climate_twin)



            weather_encounter = ClimateEncounter(
                                home_weather_profile.wind_direction,
                                home_weather_profile.wind_speed,
                                home_weather_profile.pressure,
                                home_weather_profile.humidity,
                                climate_twin_weather_profile.wind_direction,
                                climate_twin_weather_profile.wind_speed,
                                climate_twin_weather_profile.pressure,
                                climate_twin_weather_profile.humidity
                            )

            weather_messages = weather_encounter.combine_messages()

            user_instance = request.user

            climate_twin_location_instance = models.ClimateTwinLocation.create_from_dicts(
                user_instance, climate_places.climate_twin, weather_messages,
                home_location=home_location_instance
            )

            climate_twin_location_instance.save()
 

            user_visit_record_instance = UserVisit(user=user_instance, location_name=climate_twin_location_instance.name, 
                                                   location_latitude=climate_twin_location_instance.latitude,
                                                   location_longitude=climate_twin_location_instance.longitude,
                                                   visit_created_on=climate_twin_location_instance.created_on)
            user_visit_record_instance.save()

            osm_api = OpenMapAPI()
            osm_results = osm_api.find_ancient_ruins(climate_twin_weather_profile.latitude, climate_twin_weather_profile.longitude, radius=100000, num_results=15)
            nearby_ruins = osm_api.format_ruins_with_wind_compass_for_post(osm_results, climate_twin_weather_profile.wind_direction)

            for name, ruin in nearby_ruins.items():



                formatted_ruin = {
                    "name": name,
                    "user": request.user.id,
                    "direction_degree": ruin['direction_deg'],
                    "direction": ruin.get('direction'),
                    "miles_away": round(ruin['miles_away']),
                    "location_id": ruin['id'],
                    "latitude": ruin['latitude'],
                    "longitude": ruin['longitude'],
                    "tags": ruin["tags"],
                    "wind_compass": ruin['wind_compass'],
                    "wind_agreement_score": (round(ruin['wind_agreement_score'])),
                    "wind_harmony": ruin['wind_harmony'],
                    "street_view_image": ruin.get("street_view_image", ''),
                    "origin_location": climate_twin_location_instance.id,
                }

                serializer = serializers.ClimateTwinDiscoveryLocationSerializer(data=formatted_ruin)
                if serializer.is_valid():
                    discovery_location_instance = serializer.save(
                            user=user_instance  
                        )
                
                else:
                    return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


            return Response({'detail': 'Success! Twin location found.',
                'home_climate': climate_places.home_climate,
                'climate_twin': climate_places.climate_twin,
                'weather_messages' : weather_messages,
                'nearby_ruins': nearby_ruins,
            }, status=status.HTTP_200_OK)

        else:

            return Response({'error': 'error'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

'''


@swagger_auto_schema(method='get', operation_id='remainingGoesLeft', operation_dscription="Checks amount of trips remaining that user can make ", request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,

    ))
@api_view(['GET'])
#@throttle_classes([AnonRateThrottle, UserRateThrottle])
@authentication_classes([TokenAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_remaining_goes(request):
    """

    Gets remaining goes allowed for the day. Max amount is 5.

    """

    if request.method == 'GET':
        user = request.user 
 

        if user and not (user.is_staff or user.is_superuser): 
            today = timezone.now().date()
            daily_count = models.ArchivedTwinLocation.objects.filter(user=user, created_on__date=today).count()
            if daily_count >= 5:
                 return Response({'remaining_goes': '0'}, status=status.HTTP_200_OK)
          
            return Response({'remaining_goes': f'{5 - daily_count}'}, status=status.HTTP_200_OK)

        # Send the task to Celery for execution
        #run_climate_twin_algorithms_task(user.id, user_address) 

        return Response({'remaining_goes': 'No limit'}, status=status.HTTP_200_OK)

    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class HomeLocationsView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.HomeLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listHomeLocations', operation_description="Returns home locations.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return models.HomeLocation.objects.filter(user=self.request.user)


class HomeLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.HomeLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getHomeLocation', operation_description="Returns home location.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateHomeLocation', auto_schema=None)
    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    @swagger_auto_schema(operation_id='partialUpdateHomeLocation', auto_schema=None)
    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    @swagger_auto_schema(operation_id='deleteHomeLocation', operation_description="Deletes home location.")
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return models.HomeLocation.objects.filter(user=self.request.user)



# class TwinLocationsView(generics.ListAPIView):
#     authentication_classes = [TokenAuthentication, JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = serializers.ClimateTwinLocationSerializer
#     throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

#     @swagger_auto_schema(operation_id='listTwinLocations', operation_description="Returns climate twin locations.")
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)

#     def get_queryset(self):
#         return models.ClimateTwinLocation.objects.filter(user=self.request.user)


# class TwinLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
#     authentication_classes = [TokenAuthentication, JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = serializers.ClimateTwinLocationSerializer
#     throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

#     @swagger_auto_schema(operation_id='getTwinLocation', operation_description="Returns twin location.")
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)

#     @swagger_auto_schema(operation_id='updateTwinLocation', auto_schema=None)
#     def put(self, request, *args, **kwargs):
#         raise MethodNotAllowed('PUT')

#     @swagger_auto_schema(operation_id='partialUpdateTwinLocation', auto_schema=None)
#     def patch(self, request, *args, **kwargs):
#         raise MethodNotAllowed('PATCH')

#     @swagger_auto_schema(operation_id='deleteTwinLocation', operation_description="Deletes twin location.")
#     def delete(self, request, *args, **kwargs):
#         return super().destroy(request, *args, **kwargs)

#     def get_queryset(self):
#         return models.ClimateTwinLocation.objects.filter(user=self.request.user)


class TwinLocationView(generics.RetrieveDestroyAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ClimateTwinLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getTwinLocation', operation_description="Returns the user's climate twin location.")
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='deleteTwinLocation', operation_description="Deletes the user's climate twin location.")
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_object(self):
        return generics.get_object_or_404(models.ClimateTwinLocation, user=self.request.user)

class CurrentTwinLocationView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ClimateTwinLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getCurrentTwinLocation', operation_description="Returns the most recent twin location.")

    def get(self, request, *args, **kwargs):
        latest_location = self.get_latest_location()
        if not latest_location:
            return Response({'detail': 'You are not visiting anywhere right now.'}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(latest_location)
        return Response(serializer.data)

    def get_latest_location(self):
        user = self.request.user
        latest_location = models.ClimateTwinLocation.objects.filter(user=user).order_by('-created_on').first()

        # Check if the latest location exists and if it was created within the last two hours
        if latest_location and (timezone.now() - latest_location.created_on).total_seconds() < 3600: # 7200
            return latest_location
        else:
            return None

class MostRecentHomeLocationView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.HomeLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getMostRecentHomeLocation', operation_description="Returns the most recent home location.")

    def get(self, request, *args, **kwargs):
        latest_location = self.get_latest_location()
        if not latest_location:
            return Response({'detail': 'No recent home weather reading.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(latest_location)
        return Response(serializer.data)

    def get_latest_location(self):
        user = self.request.user
        latest_location = models.HomeLocation.objects.filter(user=user).order_by('-created_on').first()

        # Check if the latest location exists and if it was created within the last two hours
        if latest_location and (timezone.now() - latest_location.created_on).total_seconds() < 3600: #7200 
            return latest_location
        else:
            return None
        

class DiscoveryLocationsView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ClimateTwinDiscoveryLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listDiscoveryLocations', operation_description="Returns discovery locations.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_id='createDiscoveryLocationDirectly', auto_schema=None)
    def post(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def get_queryset(self):
        return (
            models.ClimateTwinDiscoveryLocation.objects
            .filter(user=self.request.user)
            .select_related('origin_location')  
        )

class DiscoveryLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ClimateTwinDiscoveryLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getDiscoveryLocation', operation_description="Returns discovery location.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateDiscoveryLocation', auto_schema=None)
    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    @swagger_auto_schema(operation_id='partialUpdateDiscoveryLocation', auto_schema=None)
    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    @swagger_auto_schema(operation_id='deleteDiscoveryLocation', operation_description="Deletes discovery location.")
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return models.ClimateTwinDiscoveryLocation.objects.filter(user=self.request.user)


class CurrentDiscoveryLocationsView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ClimateTwinDiscoveryLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listCurrentDiscoveryLocations', operation_description="Returns current discovery locations.")
    def get(self, request, *args, **kwargs):
        latest_location = self.get_latest_location(request.user)
        if not latest_location:
            return Response({'detail': 'You are not visiting anywhere right now.'}, status=status.HTTP_200_OK)
        
        latest_location_serializer = serializers.ClimateTwinLocationSerializer(latest_location)
        latest_location_data = latest_location_serializer.data

        discovery_locations = models.ClimateTwinDiscoveryLocation.objects.filter(origin_location_id=latest_location.pk).order_by('miles_away')
        if not discovery_locations:
            data = [latest_location_data]

            return Response(data)
        


        # Serialize the other discovery locations
        serializer = self.get_serializer(discovery_locations, many=True)
        discovery_locations_data = serializer.data

        # Combine the serialized data with the latest location at the top
        data = [latest_location_data] + discovery_locations_data

        return Response(data)
        

    def get_queryset(self):
        latest_location = self.get_latest_location(self.request.user)
        if latest_location:
            return models.ClimateTwinDiscoveryLocation.objects.filter(origin_location_id=latest_location.pk)
        return models.ClimateTwinDiscoveryLocation.objects.none() 

    def get_latest_location(self, user):

        latest_explore_location = models.CurrentLocation.objects.get(user=user)

        if not latest_explore_location.expired and (timezone.now() - latest_explore_location.last_accessed).total_seconds() < 3600: 
            latest_location = models.ClimateTwinLocation.objects.filter(user=user).order_by('-created_on').first()
       # if latest_location and (timezone.now() - latest_location.created_on).total_seconds() < 3600: # 7200 
            return latest_location
        else:
            latest_explore_location.expired = True
            latest_explore_location.save()
            return None



 


@swagger_auto_schema(method='post', operation_id='collectTreasure', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'item': openapi.Schema(type=openapi.TYPE_STRING, description="Key of one data item from location to serve as item base (see climatevisitor/item-choice)."),
            'descriptor': openapi.Schema(type=openapi.TYPE_STRING, description="Name of item."),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description of item, or notes about collecting it."),
            'third_data': openapi.Schema(type=openapi.TYPE_STRING, description="Additional data.")
        },
        required=['item'],
    ))

@api_view(['POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle]) 
@authentication_classes([TokenAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
@log_view_time
def collect(request):
    """
    Creates a treasure item from the user's current exploration site and saves as a Treasure instance belonging to user.
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

   
    if request.method == 'POST':
        user = request.user 
        descriptor = request.data.get('descriptor', None)
        description = request.data.get('description', None)
        item = request.data.get('item', None)
        add_data = request.data.get('third_data', None)


        if not item:
            return Response({'error': 'Item is required'}, status=status.HTTP_400_BAD_REQUEST)


        try:
            latest_explore_location = models.CurrentLocation.objects.get(user=user)
            location_dict = latest_explore_location.to_dict()


            if latest_explore_location.twin_location:

                twin_location = models.ClimateTwinLocation.objects.get(id=latest_explore_location.twin_location.id)

                location_type = 'twin_location__'
                
                location_dict[location_type + 'name'] = twin_location.name
                location_dict[location_type + 'miles_away'] = 0

            elif latest_explore_location.explore_location:

                location_type = 'explore_location__'

            else:
                return Response ({'error': 'Invalid location'}, status=status.HTTP_400_BAD_REQUEST)
            

            if item in location_dict.keys():
                item_name = location_dict[item]
                item_category = item
                
                # treasure_instance = Treasure.collect_item(
                #     user=user,
                #     location_name=location_dict[location_type + 'name'],
                #     location_country=location_dict[location_type + 'country'],
                #     location_city_name=location_dict[location_type + 'city_name'],
                #     location_state=location_dict[location_type + 'state'],
                #     miles_traveled_to_collect=location_dict[location_type + 'miles_away'],
                #     found_at_latitude=location_dict[location_type + 'latitude'],
                #     found_at_longitude=location_dict[location_type + 'longitude'],
                #     item_name=item_name,
                #     item_category=item_category,
                #     descriptor=descriptor,
                #     description=description,
                #     add_data=add_data
                # )
                treasure_instance = Treasure.collect_item(
                    user=user,
                    location_name=location_dict[location_type + 'name'],
                    location_country=location_dict[location_type + 'country'],
                    location_city_name=location_dict[location_type + 'city_name'],
                    location_state=location_dict[location_type + 'state'],
                    miles_traveled_to_collect=location_dict[location_type + 'miles_away'],
                    found_at_latitude=location_dict[location_type + 'latitude'],
                    found_at_longitude=location_dict[location_type + 'longitude'],
                    item_name=item_name,
                    item_category=item_category,
                    descriptor=descriptor,
                    description=description,
                    add_data=add_data
                )


                return Response({"detail": f"Success! Item '{item}' is present in the dictionary with value: {item_name}",
                                "treasure": treasure_instance.id}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": f"Item '{item}' not found in the dictionary.", 'choices': location_dict}, status=status.HTTP_404_NOT_FOUND)

        except models.CurrentLocation.DoesNotExist:
            return Response({'detail': 'Explore location not found for the user.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@swagger_auto_schema(method='get', operation_id='getItemChoices')
@api_view(['GET'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@authentication_classes([TokenAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
@log_view_time
def item_choices(request):
    """
    Returns all data from the user's most recently chosen exploration site that can be used as the item base to build an item. 

    This data can be used to build a corresponding interactive front end visual, and will be added to in future versions.
    
    Use this endpoint to populate a dropdown/selection menu.
    """

    if request.method == 'GET':
        user = request.user 

        
        try:
            latest_explore_location = models.CurrentLocation.objects.get(user=user)

            if not latest_explore_location.expired and (latest_explore_location.twin_location or latest_explore_location.explore_location):

                # if (timezone.now() - latest_explore_location.last_accessed).total_seconds() < 3600: # changed to 1 hr for testing 7200
                location_dict = latest_explore_location.to_dict()
                return Response({'choices': location_dict, 'message': 'choose one.'}, status=status.HTTP_200_OK)
            
                # latest_explore_location.expired = True
                # latest_explore_location.save() 
                
            return Response({'detail': 'You must be at an explore site to collect a treasure.'}, status=status.HTTP_200_OK)

        except models.CurrentLocation.DoesNotExist:
            return Response({'detail': 'Explore location not found for the user.'}, status=status.HTTP_404_NOT_FOUND)
        
    return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# For current demo

@swagger_auto_schema(method='get', operation_id='getClimateTwinPerformance')
@api_view(['GET'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@authentication_classes([TokenAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def key_data(request): 

    if request.method == 'GET':
        user = request.user 
        climate_twin_locations_with_home = models.ClimateTwinLocation.objects.filter(home_location__isnull=False)

        performance_data = []
        for twin_location in climate_twin_locations_with_home:
            home_location = twin_location.home_location
            temperature_difference = twin_location.temperature - home_location.temperature
            temperature_difference = round(temperature_difference, 2)
            humidity_difference = twin_location.humidity - home_location.humidity
            performance_data.append({
                'home_location_name': home_location.name,
                'twin_location_name': twin_location.name,
                'temperature_difference': temperature_difference,
                'humidity_difference': humidity_difference,
                'date_and_time': twin_location.created_on
            })


        return Response({'performance': performance_data}, status=status.HTTP_200_OK)

    return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



class CreateOrUpdateCurrentLocationView(TimedAPIView, generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CurrentLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]
    
    @swagger_auto_schema(operation_id='createCurrentLocation', operation_description="Creates explore location.")
    def post(self, request, *args, **kwargs): 

        user = request.user 
        explore_location_pk = request.data.get('explore_location')
        twin_location_pk = request.data.get('twin_location')


        if twin_location_pk:

            try:
                twin_location = models.ClimateTwinLocation.objects.get(pk=twin_location_pk, user=user)
            except models.ClimateTwinLocation.DoesNotExist:
                return Response({'error': 'The twin location does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
           
            # instead of self.update, otherwise can't access newly saved object when sending update to celery
            saved_instance = models.CurrentLocation.update_or_create_location(user, twin_location=twin_location, base_location=twin_location)


            
            last_accessed_str = saved_instance.last_accessed.isoformat()

            try:

                extra_coverage_cache_location_update(
                    user_id=user.id, 
                    state='exploring',
                    base_location=saved_instance.base_location.id,
                    location_id=saved_instance.twin_location.id,
                    name=saved_instance.twin_location.name, 
                    latitude=saved_instance.twin_location.latitude,
                    longitude=saved_instance.twin_location.longitude, 
                    last_accessed=last_accessed_str)
                
            except Exception as e:
                # FOR DEBUGGING
                push_expiration_task_scheduled(user.id, f'Could not cache new location: {e}')
                
         
            try:
                send_location_update_to_celery(user_id=user.id, state='exploring', base_location=saved_instance.base_location.id, location_id=saved_instance.twin_location.id, # = location_visiting_id
                                               location_same_as_last_update=None,
                                               temperature=saved_instance.twin_location.temperature, 
                                               name=saved_instance.twin_location.name, 
                                               latitude=saved_instance.twin_location.latitude,
                                                longitude=saved_instance.twin_location.longitude, 
                                                last_accessed=last_accessed_str)
            except Exception as e:
                print(f"Error sending location update to Celery: {str(e)}")  # Print the error to the console/log
                push_expiration_task_scheduled(user.id, f'Could not send new location to celery: {e}')
    
                return Response({'error': f'Error sending location update to Celery: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            schedule_expiration_task.apply_async(args=[user.id])
            return Response(self.get_serializer(saved_instance).data, status=status.HTTP_200_OK)

        else:

            try:
                explore_location = models.ClimateTwinDiscoveryLocation.objects.get(pk=explore_location_pk, user=user)
            except models.ClimateTwinDiscoveryLocation.DoesNotExist: 
                return Response({'error': 'The explore location does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            # instead of self.update, otherwise can't access newly saved object when sending update to celery
            saved_instance =  models.CurrentLocation.update_or_create_location(user, explore_location=explore_location)
            
            # FOR DEBUGGING
            # push_expiration_task_scheduled(user.id, 'RAN UPDATE OR CREATE LOCATION')
            last_accessed_str = saved_instance.last_accessed.isoformat()        
            
            try:
                send_location_update_to_celery(user_id=user.id, state='exploring', base_location=saved_instance.base_location.id, location_id=saved_instance.explore_location.id, # = location_visiting_id
                                                location_same_as_last_update=None,
                                                temperature= None, 
                                                name=saved_instance.explore_location.name, 
                                                latitude=saved_instance.explore_location.latitude,
                                                longitude=saved_instance.explore_location.longitude, 
                                                last_accessed=last_accessed_str)
                
                
            except Exception as e:
                print(f"Error sending location update to Celery: {str(e)}")  # Print the error to the console/log
    
                return Response({'error': f'Error sending location update to Celery: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            #schedule_expiration_task(user_id=user.id)
            schedule_expiration_task.apply_async(args=[user.id])
            return Response(self.get_serializer(saved_instance).data, status=status.HTTP_200_OK)
        
    def update_or_create_location(self, user, explore_location=None, twin_location=None, lifetime=3600):
        """
        Helper method to update or create the CurrentLocation for the user.
        It checks whether the user already has a current location and updates it or creates a new one.
        """
        # You can decide which location to set, based on what's provided
        current_location, created = models.CurrentLocation.objects.update_or_create(
            user=user,
            defaults={
                'explore_location': explore_location,
                'twin_location': twin_location,
                'expired': False  # You can set this based on your requirements
            }
        )
 
        # doesn't seem to be running
        # try:
        #     push_expiration_task_scheduled(user.id, 'INITIATING IN UPDATE CREATE METHOD')
        #     schedule_expiration_task.apply_async(args=[user.id, lifetime])
        # except Exception as e:
        #     push_expiration_task_scheduled(user.id, 'FAILED TO SCHEDULE EXPIRATION TASK')
        #     pass

        # You can perform any other operations if needed, for example, logging or tracking events
        return Response(self.get_serializer(current_location).data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return models.CurrentLocation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)  # Save user ID implicitly



class ExpireCurrentLocationView(TimedAPIView, generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CurrentLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='expireCurrentLocation', operation_description="Expires the current location immediately.")
    def patch(self, request, *args, **kwargs):
        user = request.user
 

        try:
            current_location = models.CurrentLocation.objects.get(user=user)
        except models.CurrentLocation.DoesNotExist:
            return Response({'error': 'No current location found.'}, status=status.HTTP_404_NOT_FOUND)
 


        return self.update_or_create_location(user, explore_location=None, twin_location=None, lifetime=0)

  
    def update_or_create_location(self, user, explore_location=None, twin_location=None, lifetime=0):
        """
        Updates or creates the CurrentLocation for the user and sets it to expire immediately.
        """
        current_location, created = models.CurrentLocation.objects.update_or_create(
            user=user,
            defaults={
                'explore_location': explore_location,
                'twin_location': twin_location,
                'expired': True  # Mark location as expired
            }
        )

        if current_location.expired: #check to make sure location was successfully expired, I don't want socket cache to be able
            # to fall out of sync with DB


            
            # Do I need to remove the lock if it is successfully getting deleted now in the process climate twin request task?
            remove_twin_search_lock(user.id)

            try:
                send_home_location_update_to_celery(user_id=user.id)
            except Exception as e:
                print(f"Error sending go-home location update to Celery: {str(e)}")  # Print the error to the console/log

        return Response(self.get_serializer(current_location).data, status=status.HTTP_200_OK)


class CurrentLocationView(TimedAPIView, generics.GenericAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CurrentLocationWithObjectsSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getCurrentLocation', operation_description="Returns the current location, or message that it has expired.")
    def get(self, request, *args, **kwargs):
        user = request.user

        # Try to get the current location for the user
        current_location = models.CurrentLocation.objects.filter(user=user).first()

        if current_location is None:
            return Response({'message': 'User is home.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the location has already expired
        if current_location.expired:
            return Response({'message': 'User is home.'}, status=status.HTTP_200_OK)

#(timezone.now() - latest_location.created_on).total_seconds() < 7200
        # Check if the current location has expired (based on the last_accessed time)
        if (timezone.now() - current_location.last_accessed).total_seconds() > 3600: # (changed to 1 for testing) Check if 2 hours have passed
            current_location.expired = True
            current_location.save()  # Update the expired field if it's expired
            return Response({'message': 'User is home.'}, status=status.HTTP_200_OK)

        # Return the current location data using the serializer
        return Response(self.get_serializer(current_location).data, status=status.HTTP_200_OK)
    



class ClimateTwinStatsPagination(PageNumberPagination):
    page_size = 30  
    page_size_query_param = 'page_size'
    max_page_size = 100   


class ClimateTwinSearchStatsView(TimedAPIView, generics.ListAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ClimateTwinSearchStatsSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]
    pagination_class = ClimateTwinStatsPagination 

    @swagger_auto_schema(operation_id='listClimateTwinSearchStats', operation_description="Returns climate twin search stats.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return models.ClimateTwinSearchStats.objects.filter(user=self.request.user)


@api_view(['POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle]) 
@authentication_classes([TokenAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def clean_old_discoveries_locations(request):
    """
    Admin view to archive and delete a limited number of expired discovery locations.

    WARNING: goes thru all of them regardless of if associated with expired / non expired current location
    WARNING TWO: comment out delete method of discovery location model first or you will duplicate them 
    may have done that. with the first 45k. should be 27k. mmh.
    """

    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    user = request.user 

    if not user or not user.is_superuser:
        return Response({'Error': 'Not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Set the number of items to process per request (e.g., 500)
    items_to_process = 2000

    # Query the discovery locations (no need for pagination)
    all_discovery_locations = models.ClimateTwinDiscoveryLocation.objects.select_related('origin_location').all()
    all_archived_locations = models.ArchivedDiscoveryLocation.objects.all()
    
    total_locations = len(all_discovery_locations)
    total_archived_locations = len(all_archived_locations)
    print(f'Total discovery locations in DB: {total_locations}')
    print(f'Total archived discovery locations in DB: {total_archived_locations}')

    if not all_discovery_locations.exists():
        return Response({'detail': 'No discovery locations to check.'}, status=status.HTTP_200_OK)

    # Process only the first 'items_to_process' discovery locations
    discovery_locations_to_process = all_discovery_locations[:items_to_process]

    archived_count = 0

    for location in discovery_locations_to_process: 
        models.ArchivedDiscoveryLocation.objects.create(
            user=location.user,
            name=location.name,
            explore_type=location.explore_type,
            direction_degree=location.direction_degree,
            direction=location.direction,
            miles_away=location.miles_away,
            location_id=location.location_id,
            latitude=location.latitude,
            longitude=location.longitude,
            tags=location.tags,
            wind_compass=location.wind_compass,
            wind_agreement_score=location.wind_agreement_score,
            wind_harmony=location.wind_harmony,
            street_view_image=location.street_view_image,
            created_on=location.created_on,
            last_accessed=location.last_accessed
        )

        location.delete()
        archived_count += 1

    print(f"Total archived and deleted discovery locations: {archived_count}")
    
    return Response({
        'detail': f'Successfully archived and deleted {archived_count} expired discovery locations.'
    }, status=status.HTTP_200_OK)




@api_view(['POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle]) 
@authentication_classes([TokenAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def clean_old_twin_locations(request):
    """
    Admin view to archive and delete a limited number of expired discovery locations.

    WARNING: goes thru all of them regardless of if associated with expired / non expired current location
    WARNING TWO: comment out delete method of discovery location model first or you will duplicate them 
    may have done that. with the first 45k. should be 27k. mmh.
    """

    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    user = request.user 

    if not user or not user.is_superuser:
        return Response({'Error': 'Not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Set the number of items to process per request (e.g., 500)
    items_to_process = 2000

    # Query the discovery locations (no need for pagination)
    all_twin_locations = models.ClimateTwinLocation.objects.all()
    all_archived_locations = models.ArchivedTwinLocation.objects.all()
    
    total_locations = len(all_twin_locations)
    total_archived_locations = len(all_archived_locations)
    print(f'Total twin locations in DB: {total_locations}')
    print(f'Total archived twin locations in DB: {total_archived_locations}')

    if not all_twin_locations.exists():
        return Response({'detail': 'No twin locations to check.'}, status=status.HTTP_200_OK)

    # Process only the first 'items_to_process' discovery locations
    twin_locations_to_process = all_twin_locations[:items_to_process]

    archived_count = 0

    for location in twin_locations_to_process: 
        models.ArchivedTwinLocation.objects.create(
            user=location.user,
            name=location.name,
            explore_type=location.explore_type,
            temperature=location.temperature,
            description=location.description,
            wind_speed=location.wind_speed,
            wind_direction=location.wind_direction,
            humidity=location.humidity,
            pressure=location.pressure,
            cloudiness=location.cloudiness,
            sunrise_timestamp=location.sunrise_timestamp,
            sunset_timestamp=location.sunset_timestamp,
            latitude=location.latitude,
            longitude=location.longitude,
            country=location.country or None,
            city_name=location.city_name or None,
            state=location.state or None,
            home_location=location.home_location,
            wind_friends=location.wind_friends,
            special_harmony=location.special_harmony,
            details=location.details,
            experience=location.experience,
            wind_speed_interaction=location.wind_speed_interaction,
            pressure_interaction=location.pressure_interaction,
            humidity_interaction=location.humidity_interaction,
            stronger_wind_interaction=location.stronger_wind_interaction,
        
        )

        location.delete()
        archived_count += 1

    print(f"Total archived and deleted twin locations: {archived_count}")
    
    return Response({
        'detail': f'Successfully archived and deleted {archived_count} expired twin locations.'
    }, status=status.HTTP_200_OK)