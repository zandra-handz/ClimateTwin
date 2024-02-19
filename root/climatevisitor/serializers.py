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

    def create(self, validated_data):
        # Get the current user from the context
        user = self.context['request'].user
        # Add the current user to the validated data
        validated_data['user'] = user
        # Create and return the instance
        return super().create(validated_data)



class ClimateTwinDiscoveryLocationSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.ClimateTwinDiscoveryLocation
        fields = "__all__"



class ClimateTwinExploreDiscoveryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClimateTwinExploreDiscoveryLocation
        fields = '__all__'
        read_only_fields = ['user']  # Mark the user field as read-only

    def create(self, validated_data):
        # Automatically associate the user with the object during creation
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

