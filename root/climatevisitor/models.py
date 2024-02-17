from collections.abc import Mapping
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
    special_harmony = models.BooleanField(default=False)
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
    wind_harmony = models.BooleanField(default=False)
    street_view_image = models.URLField(blank=True, null=True, default='')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    origin_location = models.ForeignKey(ClimateTwinLocation, on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        verbose_name = "Discovery Location"
        verbose_name_plural = "Discovery Locations"

    def __str__(self):
        return f"Discovery Location: {str(self.name)}, {self.pk}"



class ClimateTwinExploreDiscoveryLocation(models.Model):
    user = models.ForeignKey(BadRainbowzUser, on_delete=models.CASCADE)
    explore_location = models.ForeignKey(ClimateTwinDiscoveryLocation, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Explored Discovery Location"
        verbose_name_plural = "Explored Discovery Locations"




    def to_dict(self, prefix='', processed_fields=None):
        """
        Convert the fields of the instance and the related explore_location into a dictionary dynamically.
        """
        if processed_fields is None:
            processed_fields = set()

        fields_dict = {}

        # Include fields from the ClimateTwinExploreDiscoveryLocation model
        for field in self._meta.fields:
            field_name = field.name

            if field_name in processed_fields:
                continue

            field_value = getattr(self, field_name)

            if isinstance(field_value, Mapping):
                # Handle nested dictionary
                processed_fields.add(field_name)
                nested_dict = field_value
                for nested_key, nested_value in nested_dict.items():
                    nested_field_name = f'{field_name}__{nested_key}'
                    fields_dict[f'{prefix}{nested_field_name}'] = str(nested_value)
            else:
                fields_dict[f'{prefix}{field_name}'] = str(field_value)

        # Include fields from the related ClimateTwinDiscoveryLocation model
        if self.explore_location:
            for field in self.explore_location._meta.fields:
                field_name = field.name

                if field_name in processed_fields:
                    continue

                field_value = getattr(self.explore_location, field_name)

                if isinstance(field_value, Mapping):
                    # If the field value is a dictionary, gather its keys and values
                    processed_fields.add(field_name)
                    nested_dict = field_value
                    for nested_key, nested_value in nested_dict.items():
                        nested_field_name = f'{field_name}__{nested_key}'
                        fields_dict[f'{prefix}explore_location__{nested_field_name}'] = str(nested_value)
                else:
                    fields_dict[f'{prefix}explore_location__{field_name}'] = str(field_value)

        return fields_dict

    def to_dict_old(self):
        """
        Convert the fields of the instance and the related explore_location into a dictionary dynamically.
        """
        fields_dict = {}

        # Include fields from the ClimateTwinExploreDiscoveryLocation model
        for field in self._meta.fields:
            field_name = field.name
            field_value = getattr(self, field_name)
            fields_dict[field_name] = str(field_value)

        # Include fields from the related ClimateTwinDiscoveryLocation model
        if self.explore_location:
            for field in self.explore_location._meta.fields:
                field_name = field.name
                field_value = getattr(self.explore_location, field_name)
                fields_dict[f'explore_location__{field_name}'] = str(field_value)

        return fields_dict

    def __str__(self):
        return f"Explored Discovery Location: {str(self.name)}, {self.pk}"

