from . import models
from rest_framework import serializers  


class ClimateTwinLocationSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.ClimateTwinLocation
        fields = "__all__"


class HomeLocationSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.HomeLocation
        fields = "__all__"


class CurrentLocationMatchSerializer(serializers.Serializer):
    twin_instance = ClimateTwinLocationSerializer()
    home_instance = HomeLocationSerializer(required=False)  # Make home_instance optional


class ClimateTwinDiscoveryLocationSerializer(serializers.ModelSerializer):

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
    
    
