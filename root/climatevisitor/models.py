from django.db import models
from users.models import BadRainbowzUser  


# Create your models here.

class ClimateTwinLocation(models.Model):
    user = models.ForeignKey(BadRainbowzUser, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, default="")
    temperature = models.FloatField(default=0.0)
    description = models.CharField(max_length=255, default="")
    wind_speed = models.FloatField(default=0.0)
    wind_direction = models.IntegerField(default=0)
    humidity = models.IntegerField(default=0)
    pressure = models.IntegerField(default=0)
    cloudiness = models.IntegerField(default=0)
    sunrise_timestamp = models.BigIntegerField(default=0)
    sunset_timestamp = models.BigIntegerField(default=0)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    wind_friends = models.CharField(max_length=255, default="")
    details = models.TextField(default="")
    experience = models.TextField(default="")
    wind_speed_interaction = models.TextField(default="")
    pressure_interaction = models.TextField(default="")
    humidity_interaction = models.TextField(default="")
    stronger_wind_interaction = models.CharField(max_length=255, default="")

    @classmethod
    def create_from_dicts(cls, user, climate_twin, weather_messages):

        address = list(climate_twin.keys())[0]
        climate_data = climate_twin[address]
        
        interaction = list(weather_messages.keys())[0]
        interaction_data = weather_messages[interaction]

        weather_data = cls(user=user, name=address, **climate_data, **interaction_data)
        return weather_data


    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return f"Location: {str(self.name)}, {self.pk}"



class ClimateTwinDiscoveryLocation(models.Model):
    user = models.ForeignKey(BadRainbowzUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default='Unnamed Ruin')
    direction_degree = models.FloatField(default=0.0)
    direction = models.CharField(max_length=255, default='Unknown')
    miles_away = models.FloatField(default=0.0)
    location_id = models.CharField(max_length=255, default='')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    tags = models.JSONField(default=dict)
    wind_compass = models.CharField(max_length=255, default='')
    wind_agreement_score = models.IntegerField(default=0)
    street_view_image = models.URLField(blank=True, null=True, default='')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Discovery Location"
        verbose_name_plural = "Discovery Locations"

    def __str__(self):
        return f"Discovery Location: {str(self.name)}, {self.pk}"



'''
To inititialize:

from django.utils import timezone

location_instance = ClimateTwinLocation(
    user=user,  # Replace with the actual user instance
    name=str(formatted_ruin),  # Store the formatted_ruin as a string in the 'name' field
    direction_deg=formatted_ruin.get('direction_deg', 0.0),
    direction=formatted_ruin.get('direction', 'Unknown'),
    miles_away=formatted_ruin.get('miles_away', 0.0),
    location_id=formatted_ruin.get('id', ''),
    latitude=formatted_ruin.get('latitude', 0.0),
    longitude=formatted_ruin.get('longitude', 0.0),
    tags=formatted_ruin.get('tags', {}),
    wind_compass=formatted_ruin.get('wind_compass', ''),
    wind_agreement_score=formatted_ruin.get('wind_agreement_score', 0),
    street_view_image=formatted_ruin.get('street_view_image', ''),
    creation_date=timezone.now(),
    last_accessed=timezone.now()
)

# Save the instance
location_instance.save()


'''