from rest_framework import serializers
from .models import ClimateTwinLocation


class ClimateTwinLocationSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = ClimateTwinLocation
        fields = "__all__"
