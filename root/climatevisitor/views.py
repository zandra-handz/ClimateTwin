from . import models
from . import serializers
from .climatetwinclasses.ClimateEncounterClass import ClimateEncounter
from .climatetwinclasses.ClimateObjectClass import ClimateObject
from .climatetwinclasses.ClimateTwinFinderClass import ClimateTwinFinder
from .climatetwinclasses.OpenMapAPIClass import OpenMapAPI
from django.shortcuts import render
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, status, throttling
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, parser_classes, throttle_classes, permission_classes, schema
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from users.models import Treasure, UserVisit

# Create your views here.
@swagger_auto_schema(operation_id='index')
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def index(request):
    return render(request, 'index.html', {})


@swagger_auto_schema(operation_id='endpoints')
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def endpoints(request):
    return render(request, 'endpoints.html', {})




@swagger_auto_schema(method='post', order=1, operation_id='createGo', operation_dscription="Main feature of app", request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'address': openapi.Schema(type=openapi.TYPE_STRING, description="User's current address. Must be a valid address.")
        },
        required=['address'],
    ))
@api_view(['POST'])
#@throttle_classes([AnonRateThrottle, UserRateThrottle])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
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

        # Check if user has hit daily limit
        if user and not (user.is_staff or user.is_superuser): 
            today = timezone.now().date()
            daily_count = models.ClimateTwinLocation.objects.filter(user=user, creation_date__date=today).count()
            if daily_count >= 3:
                return Response({'error': 'You have reached the daily limit of visits.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create 
        climate_places = ClimateTwinFinder(user_address)

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
                user_instance, climate_places.climate_twin, weather_messages
            )

            climate_twin_location_instance.save()

            user_visit_record_instance = UserVisit(user=user_instance, location_name=climate_twin_location_instance.name, 
                                                   location_latitude=climate_twin_location_instance.latitude,
                                                   location_longitude=climate_twin_location_instance.longitude,
                                                   visit_datetime=climate_twin_location_instance.creation_date)
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


            return Response({"detail": "Success! Twin location found.",
                'home_climate': climate_places.home_climate,
                'climate_twin': climate_places.climate_twin,
                'weather_messages' : weather_messages,
                'nearby_ruins': nearby_ruins,
            }, status=status.HTTP_200_OK)

        else:

            return Response({'error': 'error'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ClimateTwinLocationsView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.ClimateTwinLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listTwinLocations', operation_description="Returns climate twin locations.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_id='createTwinLocationDirectly', auto_schema=None)
    def post(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def get_queryset(self):
        return models.ClimateTwinLocation.objects.filter(user=self.request.user)


class ClimateTwinLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.ClimateTwinLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getTwinLocation', operation_description="Returns twin location.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateTwinLocation', auto_schema=None)
    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    @swagger_auto_schema(operation_id='partialUpdateTwinLocation', auto_schema=None)
    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    @swagger_auto_schema(operation_id='deleteTwinLocation', operation_description="Deletes twin location.")
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return models.ClimateTwinLocation.objects.filter(user=self.request.user)



class CurrentClimateTwinLocationView(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.ClimateTwinLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getCurrentTwinLocation', operation_description="Returns the most recent twin location.")

    def get(self, request, *args, **kwargs):
        latest_location = self.get_latest_location()
        if not latest_location:
            return Response({'detail': 'You are not visiting anywhere right now.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(latest_location)
        return Response(serializer.data)

    def get_latest_location(self):
        user = self.request.user
        latest_location = models.ClimateTwinLocation.objects.filter(user=user).order_by('-creation_date').first()

        # Check if the latest location exists and if it was created within the last two hours
        if latest_location and (timezone.now() - latest_location.creation_date).total_seconds() < 7200: 
            return latest_location
        else:
            return None
        

class ClimateTwinDiscoveryLocationsView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.ClimateTwinDiscoveryLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listDiscoveryLocations', operation_description="Returns discovery locations.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_id='createDiscoveryLocationDirectly', auto_schema=None)
    def post(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def get_queryset(self):
        return models.ClimateTwinDiscoveryLocation.objects.filter(user=self.request.user)
    


class ClimateTwinDiscoveryLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]
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


class CurrentClimateTwinDiscoveryLocationsView(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.ClimateTwinDiscoveryLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listCurrentDiscoveryLocations', operation_description="Returns current discovery locations.")
    def get(self, request, *args, **kwargs):
        latest_location = self.get_latest_location(request.user)
        if not latest_location:
            return Response({'detail': 'You are not visiting anywhere right now.'}, status=status.HTTP_404_NOT_FOUND)
        discovery_locations = models.ClimateTwinDiscoveryLocation.objects.filter(origin_location=latest_location)
        serializer = self.get_serializer(discovery_locations, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return models.ClimateTwinDiscoveryLocation.objects.filter(user=self.request.user)

    def get_latest_location(self, user):
        latest_location = models.ClimateTwinLocation.objects.filter(user=user).order_by('-creation_date').first()
        if latest_location and (timezone.now() - latest_location.creation_date).total_seconds() < 7200: 
            return latest_location
        else:
            return None

class ClimateTwinExploreDiscoveryLocationsView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.ClimateTwinExploreDiscoveryLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listExploreLocations', operation_description="Returns explore locations.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_id='createExploreLocation', operation_description="Creates explore location.")
    def post(self, request, *args, **kwargs):
        explore_location_pk = request.data.get('explore_location')
        try:
            explore_location = models.ClimateTwinDiscoveryLocation.objects.get(pk=explore_location_pk)
            explore_location_creation_date = explore_location.creation_date
            if (timezone.now() - explore_location_creation_date).total_seconds() >= 7200:
                return Response({'error': 'The explore location must have been created within the last two hours.'}, status=status.HTTP_400_BAD_REQUEST)
        except models.ClimateTwinDiscoveryLocation.DoesNotExist:
            return Response({'error': 'The explore location does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return models.ClimateTwinExploreDiscoveryLocation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ClimateTwinExploreDiscoveryLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.ClimateTwinExploreDiscoveryLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getExploreLocation', operation_description="Returns explore location.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateExploreLocation', auto_schema=None)
    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    @swagger_auto_schema(operation_id='partialUpdateExploreLocation', auto_schema=None)
    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    @swagger_auto_schema(operation_id='deleteExploreLocation', operation_description="Deletes explore location.")
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return models.ClimateTwinExploreDiscoveryLocation.objects.filter(user=self.request.user)


class CurrentClimateTwinExploreDiscoverLocationView(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.ClimateTwinExploreDiscoveryLocationSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getCurrentExploreDiscoverLocation', operation_description="Returns the most recent explore location.")
    def get(self, request, *args, **kwargs):
        latest_location = self.get_latest_location(request.user)
        if not latest_location:
            return Response({'detail': 'You are not exploring any locations right now.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(latest_location)
        return Response(serializer.data)

    def get_latest_location(self, user):
        most_recent_climate_twin_location = models.ClimateTwinLocation.objects.filter(user=user).order_by('-creation_date').first()
        if not most_recent_climate_twin_location:
            return None
        
        latest_location = models.ClimateTwinExploreDiscoveryLocation.objects.filter(user=user).order_by('-creation_date').first()
        
        if latest_location and latest_location.explore_location.original_location == most_recent_climate_twin_location.pk and \
           (timezone.now() - latest_location.creation_date).total_seconds() < 7200: 
            return latest_location
        else:
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

@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def collect(request):
    """
    Creates a treasure item from the user's current exploration site and saves as a Treasure instance belonging to user.
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    if request.method == 'GET':
        user = request.user 

        try:
            # Retrieve the most recently created ClimateTwinExploreDiscoveryLocation instance by the user
            latest_explore_location = models.ClimateTwinExploreDiscoveryLocation.objects.filter(user=user).latest('creation_date')
            location_id = latest_explore_location.explore_location.id
            
            location = models.ClimateTwinDiscoveryLocation.objects.get(id=location_id)
            serializer = serializers.ClimateTwinDiscoveryLocationSerializer(location)
            serialized_data = serializer.data

            return Response({'key_value_pairs': serialized_data, 'message': 'Select an item and add a note.'}, status=status.HTTP_200_OK)

        except models.ClimateTwinExploreDiscoveryLocation.DoesNotExist:
            return Response({'detail': 'Explore location not found for the user.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        user = request.user 
        descriptor = request.data.get('descriptor', None)
        description = request.data.get('description', None)
        item = request.data.get('item', None)
        add_data = request.data.get('third_data', None)


        if not item:
            return Response({'error': 'Item is required'}, status=status.HTTP_400_BAD_REQUEST)


        try:
            # Retrieve the most recently created ClimateTwinExploreDiscoveryLocation instance by the user
            latest_explore_location = models.ClimateTwinExploreDiscoveryLocation.objects.filter(user=user).latest('creation_date')
            location_dict = latest_explore_location.to_dict()

            # Check if the entered item is in the dictionary
            if item in location_dict.keys():
                item_name = location_dict[item]
                item_category = item

                # Create and save a Treasure instance using collect_item function
                
                treasure_instance = Treasure.collect_item(
                    user=user,
                    location_name=location_dict['explore_location__name'],
                    miles_traveled_to_collect=location_dict['explore_location__miles_away'],
                    found_at_latitude=location_dict['explore_location__latitude'],
                    found_at_longitude=location_dict['explore_location__longitude'],
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

        except models.ClimateTwinExploreDiscoveryLocation.DoesNotExist:
            return Response({'detail': 'Explore location not found for the user.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@swagger_auto_schema(method='get', operation_id='getItemChoices')
@api_view(['GET'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def item_choices(request):
    """
    Returns all data from the user's most recently chosen exploration site that can be used as the item base to build an item. 
    
    Use this endpoint to populate a dropdown/selection menu.
    """

    if request.method == 'GET':
        user = request.user 

        
        try:
            latest_explore_location = models.ClimateTwinExploreDiscoveryLocation.objects.filter(user=user).latest('creation_date')
            location_dict = latest_explore_location.to_dict()

            return Response({'choices': location_dict, 'message': 'choose one.'}, status=status.HTTP_200_OK)

        except models.ClimateTwinExploreDiscoveryLocation.DoesNotExist:
            return Response({'detail': 'Explore location not found for the user.'}, status=status.HTTP_404_NOT_FOUND)
        
    return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

