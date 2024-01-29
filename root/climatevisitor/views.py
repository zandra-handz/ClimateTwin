from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import ClimateTwinLocation
from .serializers import ClimateTwinLocationSerializer

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

            # Assuming you have climate_places.climate_twin and weather_messages available
            climate_twin_location_instance = ClimateTwinLocation.create_from_dicts(
                user_instance, climate_places.climate_twin, weather_messages
            )

            # Save the instance to the database
            climate_twin_location_instance.save()

            osm_api = OpenMapAPI()
            osm_results = osm_api.find_ancient_ruins(climate_twin_weather_profile.latitude, climate_twin_weather_profile.longitude, radius=100000, num_results=15)
            nearby_ruins = osm_api.format_ruins_with_wind_compass_for_post(osm_results, climate_twin_weather_profile.wind_direction)


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
        # Filter locations based on the logged-in user
        return ClimateTwinLocation.objects.filter(user=self.request.user)
    
class ClimateTwinLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinLocationSerializer

    def get_queryset(self):
        # Filter locations based on the logged-in user
        return ClimateTwinLocation.objects.filter(user=self.request.user)

class ClimateTwinLocationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinLocationSerializer

    def get_queryset(self):
        # Filter locations based on the logged-in user
        return ClimateTwinLocation.objects.filter(user=self.request.user)