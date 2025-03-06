from . import models
from rest_framework import serializers  




class HomeLocationSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.HomeLocation
        fields = "__all__"


class ClimateTwinLocationSerializer(serializers.ModelSerializer):

    home_location = HomeLocationSerializer(read_only=True)

    class Meta(object):
        model = models.ClimateTwinLocation
        fields = "__all__"



class CurrentLocationMatchSerializer(serializers.Serializer):
    twin_instance = ClimateTwinLocationSerializer()
    home_instance = HomeLocationSerializer(required=False)  # Make home_instance optional


class ClimateTwinDiscoveryLocationSerializer(serializers.ModelSerializer):

    origin_location = ClimateTwinLocationSerializer(read_only=True)

    class Meta(object):
        model = models.ClimateTwinDiscoveryLocation
        fields = "__all__"


class ClimateTwinDiscoveryLocationCreateSerializer(serializers.ModelSerializer):

     

    class Meta(object):
        model = models.ClimateTwinDiscoveryLocation
        fields = "__all__"







class ClimateTwinExploreDiscoveryLocationSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = models.ClimateTwinExploreLocation
        fields = '__all__'
        read_only_fields = ['user']  # Mark the user field as read-only

    def create(self, validated_data):
        # Automatically associate the user with the object during creation
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Custom update logic, if necessary
        instance = super().update(instance, validated_data)
        return instance
    


    

class ClimateTwinExploreDiscoveryLocationWithObjectsSerializer(serializers.ModelSerializer):

    explore_location = ClimateTwinDiscoveryLocationSerializer(read_only=True)  # Nested object
    twin_location = ClimateTwinLocationSerializer(read_only=True)  # Nested object
    class Meta:
        model = models.ClimateTwinExploreLocation
        fields = '__all__'
        read_only_fields = ['user']  # Mark the user field as read-only

    def create(self, validated_data):
        # Automatically associate the user with the object during creation
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

    
class CurrentLocationSerializer(serializers.ModelSerializer):
    # only need this when getting the data, not saving it; plus it was causing an error
    # location_id = serializers.SerializerMethodField()  # Computed field for location ID

    class Meta:
        model = models.CurrentLocation
        fields = '__all__'  # Ensures location_id is included
        read_only_fields = ['user']

    # def get_location_id(self, obj):
    #     """Return the ID of either explore_location or twin_location, whichever exists."""
    #     if obj.explore_location:
    #         return obj.explore_location.id
    #     elif obj.twin_location:
    #         return obj.twin_location.id
    #     return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        explore_location = data.get('explore_location')
        twin_location = data.get('twin_location')

        if explore_location and twin_location:
            raise serializers.ValidationError("Only one of explore_location or twin_location can be specified.")
        return data


class CurrentLocationWithObjectsSerializer(serializers.ModelSerializer):
    explore_location = ClimateTwinDiscoveryLocationSerializer(read_only=True)  # Nested object
    twin_location = ClimateTwinLocationSerializer(read_only=True)  # Nested object
    location_visiting_id = serializers.SerializerMethodField()  # Computed field for location ID

    class Meta:
        model = models.CurrentLocation
        fields = '__all__'
        read_only_fields = ['user']

    def get_location_visiting_id(self, obj):
        """Return the ID of either explore_location or twin_location, whichever exists."""
        if obj.explore_location:
            return obj.explore_location.id
        elif obj.twin_location:
            return obj.twin_location.id
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        explore_location = data.get('explore_location')
        twin_location = data.get('twin_location')

        if explore_location and twin_location:
            raise serializers.ValidationError("Only one of explore_location or twin_location can be specified.")
        return data
