from collections.abc import Mapping
from django.core.exceptions import ValidationError
from django.db import models
from users.models import BadRainbowzUser  


# Create your models here.


# HomeLocation.objects.filter(user=my_user).first()
# I think this should eventually be a one-to-one that rewrites, like current location
class HomeLocation(models.Model):
    user = models.ForeignKey(BadRainbowzUser, on_delete=models.CASCADE)
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
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

        verbose_name = "Home Location"
        verbose_name_plural = "Home Locations"

    def __str__(self):
        return f"Home Location: {str(self.name)}, {self.pk}"



class ClimateTwinLocation(models.Model):
    user = models.ForeignKey(BadRainbowzUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="")
    explore_type = models.CharField(max_length=255, default="twin_location", editable=False)
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

    home_location = models.ForeignKey(HomeLocation, on_delete=models.CASCADE, null=True, blank=True)

    wind_friends = models.CharField(max_length=255, default="")
    special_harmony = models.BooleanField(default=False)
    details = models.TextField(default="")
    experience = models.TextField(default="")
    wind_speed_interaction = models.TextField(default="")
    pressure_interaction = models.TextField(default="")
    humidity_interaction = models.TextField(default="")
    stronger_wind_interaction = models.CharField(max_length=255, default="")

    created_on = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.explore_type = "twin_location"
        super().save(*args, **kwargs)


    @classmethod
    def create_from_dicts(cls, user, climate_twin, weather_messages, home_location=None):
        address = list(climate_twin.keys())[0]
        climate_data = climate_twin[address]
        
        interaction = list(weather_messages.keys())[0]
        interaction_data = weather_messages[interaction]

        # Prepare data for the instance
        data = {
            'user': user,
            'name': address,
            **climate_data,
            **interaction_data
        }

        # Add home_location if provided
        if home_location:
            data['home_location'] = home_location

        # Create and return the instance
        return cls(**data)


    class Meta:
        ordering = ['-created_on']
        
        verbose_name = "Location"
        verbose_name_plural = "Locations"

        indexes = [
            models.Index(fields=['-created_on']),  # Index for latest queries
        ]

    def __str__(self):
        return f"Location: {str(self.name)}, {self.pk}"




class ClimateTwinDiscoveryLocation(models.Model):
    user = models.ForeignKey(BadRainbowzUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default='Unnamed Ruin')
    explore_type = models.CharField(max_length=255, default="discovery_location", editable=False)
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
    created_on = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    origin_location = models.ForeignKey(ClimateTwinLocation, on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['origin_location']),
        ]
        verbose_name = "Discovery Location"
        verbose_name_plural = "Discovery Locations"

    def __str__(self):
        return f"Discovery Location: {str(self.name)}, {self.pk}"


    def save(self, *args, **kwargs):
        if not self.pk:
            self.explore_type = "discovery_location"
        super().save(*args, **kwargs)



class ClimateTwinExploreLocation(models.Model):
    user = models.ForeignKey(BadRainbowzUser, on_delete=models.CASCADE)
    explore_location = models.ForeignKey(ClimateTwinDiscoveryLocation, on_delete=models.CASCADE, null=True, blank=True)
    twin_location = models.ForeignKey(ClimateTwinLocation, on_delete=models.CASCADE, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    expired = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']
        verbose_name = "Explored Discovery Location"
        verbose_name_plural = "Explored Discovery Locations"
        indexes = [
            models.Index(fields=['-created_on']),   
            models.Index(fields=['user', '-created_on']),   
        ]

    def clean(self):
        if self.explore_location and self.twin_location:
            raise ValidationError("Only one of explore_location or twin_location can be specified.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


    def to_dict(self, prefix='', processed_fields=None):
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

        # Include fields from the related ClimateTwinLocation model
        if self.twin_location:
            for field in self.twin_location._meta.fields:
                field_name = field.name

                if field_name in processed_fields:
                    continue

                field_value = getattr(self.twin_location, field_name)

                if isinstance(field_value, Mapping):
                    # If the field value is a dictionary, gather its keys and values
                    processed_fields.add(field_name)
                    nested_dict = field_value
                    for nested_key, nested_value in nested_dict.items():
                        nested_field_name = f'{field_name}__{nested_key}'
                        fields_dict[f'{prefix}twin_location__{nested_field_name}'] = str(nested_value)
                else:
                    fields_dict[f'{prefix}twin_location__{field_name}'] = str(field_value)

        return fields_dict


    def __str__(self):
        if self.explore_location:
            return f"Explored Discovery Location: {str(self.explore_location)}, {self.pk}"
        if self.twin_location:
            return f"Explored Discovery Location: {str(self.twin_location)}, {self.pk}"
    

class CurrentLocation(models.Model):
    user = models.OneToOneField(BadRainbowzUser, on_delete=models.CASCADE)

    # twin location
    base_location = models.ForeignKey(ClimateTwinLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='base_location_set') # needed because of the other climate twin model here, otherwise django will set the same name for both
    
    # CURRENT LOCATION (either explore or twin, other one will be empty):
    explore_location = models.ForeignKey(ClimateTwinDiscoveryLocation, on_delete=models.SET_NULL, null=True, blank=True)
    twin_location = models.ForeignKey(ClimateTwinLocation, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    expired = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']
        verbose_name = "Current Location"
        verbose_name_plural = "Current Locations"

    def clean(self):
        if self.explore_location and self.twin_location:
            raise ValidationError("Only one of explore_location or twin_location can be specified.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def to_dict(self, prefix='', processed_fields=None):
        if processed_fields is None:
            processed_fields = set()

        fields_dict = {}

        # Include fields from the CurrentLocation model
        for field in self._meta.fields:
            field_name = field.name
            if field_name in processed_fields:
                continue
            field_value = getattr(self, field_name)
            if isinstance(field_value, Mapping):
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
                    processed_fields.add(field_name)
                    nested_dict = field_value
                    for nested_key, nested_value in nested_dict.items():
                        nested_field_name = f'{field_name}__{nested_key}'
                        fields_dict[f'{prefix}explore_location__{nested_field_name}'] = str(nested_value)
                else:
                    fields_dict[f'{prefix}explore_location__{field_name}'] = str(field_value)

        # Include fields from the related ClimateTwinLocation model
        if self.twin_location:
            for field in self.twin_location._meta.fields:
                field_name = field.name
                if field_name in processed_fields:
                    continue
                field_value = getattr(self.twin_location, field_name)
                if isinstance(field_value, Mapping):
                    processed_fields.add(field_name)
                    nested_dict = field_value
                    for nested_key, nested_value in nested_dict.items():
                        nested_field_name = f'{field_name}__{nested_key}'
                        fields_dict[f'{prefix}twin_location__{nested_field_name}'] = str(nested_value)
                else:
                    fields_dict[f'{prefix}twin_location__{field_name}'] = str(field_value)

        return fields_dict
    
    @classmethod
    def update_or_create_location(cls, user, base_location=None, explore_location=None, twin_location=None):
        """
        Helper method to update or create the CurrentLocation for the user.
        It checks whether the user already has a current location and updates it or creates a new one.
        """ 
        
        if explore_location and twin_location:
            raise ValidationError("Only one of explore_location or twin_location can be specified.")
 
 
        defaults={
            #'base_location': base_location, #I don't want to overwrite if nothing is passed in
            'explore_location': explore_location,
            'twin_location': twin_location,
            'expired': False 
        }

        if base_location is not None:
            defaults['base_location'] = base_location
         

        current_location, created = cls.objects.update_or_create(
            user=user,
            defaults=defaults
        )

        return current_location

    def __str__(self):
        if self.explore_location:
            return f"Current or Most Recent Location: {str(self.explore_location)}, {self.pk}"
        if self.twin_location:
            return f"Current or Most Recent Location: {str(self.twin_location)}, {self.pk}"


class ClimateTwinSearchStats(models.Model):
    user = models.ForeignKey(BadRainbowzUser, on_delete=models.CASCADE)
    home_temperature = models.FloatField()
    home_address = models.CharField(max_length=255) 
    climate_twin_temperature = models.FloatField()
    climate_twin_address = models.CharField(max_length=255) 

    points_searched_on_land = models.IntegerField()
    countries_searched = models.IntegerField()
    total_points_generated = models.IntegerField()
    openweathermap_calls = models.IntegerField()
    google_map_calls = models.IntegerField()
    high_variances = models.IntegerField() 
     
    
    preset_random_points_in_each_country = models.IntegerField()
    preset_temp_diff_is_high_variance = models.IntegerField()
    preset_num_high_variances_allowed = models.IntegerField()
    preset_divider_for_point_gen_deviation = models.FloatField()
    preset_num_final_candidates_required = models.IntegerField()

    home_latitude = models.FloatField()
    home_longitude = models.FloatField() 
    
    climate_twin_latitude = models.FloatField()
    climate_twin_longitude = models.FloatField()

    associated_location = models.ForeignKey(ClimateTwinLocation, on_delete=models.SET_NULL, null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-id']
        # indexes = [
        #     models.Index(fields=['origin_location']),
        # ]
        verbose_name = "Twin Search Stats"
        verbose_name_plural = "Twin Search Stats"

    def __str__(self):
        return f"Twin Search Stats #{self.pk}"

 