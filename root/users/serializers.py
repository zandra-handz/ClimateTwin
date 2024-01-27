
from .models import BadRainbowzUser, CollectedItem, UserProfile, UserSettings, UserVisit
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = BadRainbowzUser
        fields = ['id', 'username', 'password', 'email', 'phone_number', 'addresses'] 


class BadRainbowzUserSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = BadRainbowzUser
        fields = ['id', 'username', 'password', 'email', 'phone_number', 'addresses']


class CollectedItemSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = CollectedItem
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = UserProfile
        fields = "__all__"


class UserSettingsSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = UserSettings
        fields = "__all__"


class UserVisitSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = UserVisit
        fields = "__all__"



        