from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
import json
from rest_framework.permissions import IsAuthenticated
from .models import ClimateTwinLocation, ClimateTwinDiscoveryLocation, ClimateTwinExploreDiscoveryLocation
from .serializers import ClimateTwinLocationSerializer, ClimateTwinDiscoveryLocationSerializer, ClimateTwinExploreDiscoveryLocationSerializer

# Create your views here.
def index(request):
    return render(request, 'index.html', {})

def endpoints(request):
    return render(request, 'endpoints.html', {})



from rest_framework.decorators import api_view, authentication_classes, throttle_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.response import Response
from rest_framework import status
from .climatetwinclasses.ClimateEncounterClass import ClimateEncounter
from .climatetwinclasses.ClimateObjectClass import ClimateObject
from .climatetwinclasses.ClimateTwinFinderClass import ClimateTwinFinder
from .climatetwinclasses.OpenMapAPIClass import OpenMapAPI


@api_view(['POST', 'GET', 'OPTIONS'])
#@throttle_classes([AnonRateThrottle, UserRateThrottle])
#@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def go(request):
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    if request.method == 'GET':
        #if not request.user.is_authenticated:
        #   return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'message': 'Enter address'}, status=status.HTTP_200_OK)

    if request.method == 'POST':
        address = request.data.get('address', None)

        if not address:
            return Response({'error': 'Address is required'}, status=status.HTTP_400_BAD_REQUEST)

        climate_places = ClimateTwinFinder(address)

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

            climate_twin_location_instance = ClimateTwinLocation.create_from_dicts(
                user_instance, climate_places.climate_twin, weather_messages
            )

            climate_twin_location_instance.save()

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

                serializer = ClimateTwinDiscoveryLocationSerializer(data=formatted_ruin)
                if serializer.is_valid():
                    discovery_location_instance = serializer.save(
                            user=user_instance  
                        )
                
                else:
                    return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



            return Response({
                'home_climate': climate_places.home_climate,
                'climate_twin': climate_places.climate_twin,
                'weather_messages' : weather_messages,
                'nearby_ruins': nearby_ruins,
            }, status=status.HTTP_200_OK)

        else:

            return Response({'error': 'error'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ClimateTwinLocationsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinLocationSerializer

    def get_queryset(self):
        return ClimateTwinLocation.objects.filter(user=self.request.user)
    
class ClimateTwinLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinLocationSerializer

    def get_queryset(self):
        return ClimateTwinLocation.objects.filter(user=self.request.user)

class ClimateTwinLocationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinLocationSerializer

    def get_queryset(self):
        return ClimateTwinLocation.objects.filter(user=self.request.user)


class ClimateTwinDiscoveryLocationsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinDiscoveryLocationSerializer

    def get_queryset(self):
        return ClimateTwinDiscoveryLocation.objects.filter(user=self.request.user)
    
class ClimateTwinDiscoveryLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinDiscoveryLocationSerializer

    def get_queryset(self):
        return ClimateTwinDiscoveryLocation.objects.filter(user=self.request.user)

class ClimateTwinDiscoveryLocationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinDiscoveryLocationSerializer

    def get_queryset(self):
        return ClimateTwinDiscoveryLocation.objects.filter(user=self.request.user)


class ClimateTwinExploreDiscoveryLocationsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinExploreDiscoveryLocationSerializer

    def get_queryset(self):
        return ClimateTwinExploreDiscoveryLocation.objects.filter(user=self.request.user)
    
class ClimateTwinExploreDiscoveryLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinExploreDiscoveryLocationSerializer

    def get_queryset(self):
        return ClimateTwinExploreDiscoveryLocation.objects.filter(user=self.request.user)

class ClimateTwinExploreDiscoveryLocationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinExploreDiscoveryLocationSerializer

    def get_queryset(self):
        return ClimateTwinExploreDiscoveryLocation.objects.filter(user=self.request.user)


@api_view(['POST', 'GET', 'OPTIONS'])
#@throttle_classes([AnonRateThrottle, UserRateThrottle])
#@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def collect(request):
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)

    if request.method == 'GET':
        user = request.user 

        try:
            # Retrieve the most recently created ClimateTwinExploreDiscoveryLocation instance by the user
            latest_explore_location = ClimateTwinExploreDiscoveryLocation.objects.filter(user=user).latest('creation_date')
            location_id = latest_explore_location.explore_location.id
            
            location = ClimateTwinDiscoveryLocation.objects.get(id=location_id)
            serializer = ClimateTwinDiscoveryLocationSerializer(location)
            serialized_data = serializer.data

            return Response({'key_value_pairs': serialized_data, 'message': 'Select key-value pair and add a note.'}, status=status.HTTP_200_OK)

        except ClimateTwinExploreDiscoveryLocation.DoesNotExist:
            return Response({'detail': 'Explore location not found for the user.'}, status=status.HTTP_404_NOT_FOUND)


    return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

