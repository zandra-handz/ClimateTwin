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

    class Meta(object):
        model = ClimateTwinExploreDiscoveryLocation
        fields = "__all__"

