
from .models import BadRainbowzUser, ItemInbox, Treasure, UserProfile, UserSettings, UserVisit
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


class TreasureSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = Treasure
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



        