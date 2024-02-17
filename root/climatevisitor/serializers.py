from rest_framework import serializers
from .models import ClimateTwinLocation, ClimateTwinDiscoveryLocation, ClimateTwinExploreDiscoveryLocation


class ClimateTwinLocationSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = ClimateTwinLocation
        fields = "__all__"


class ClimateTwinDiscoveryLocationSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = ClimateTwinDiscoveryLocation
        fields = "__all__"


class ClimateTwinExploreDiscoveryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClimateTwinDiscoveryLocation
        fields = '__all__'
        read_only_fields = ['user']  # Mark the user field as read-only

    def create(self, validated_data):
        # Automatically associate the user with the object during creation
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


