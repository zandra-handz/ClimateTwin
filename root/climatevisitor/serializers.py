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

class MatchPerformanceSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        """
        Serialize list of tuples containing twin instance and its associated home instance.
        """
        return [{
            'twin_instance': twin_instance_serializer.data,
            'home_instance': home_instance_serializer.data if home_instance_serializer else None
        } for twin_instance_serializer, home_instance_serializer in data]


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

