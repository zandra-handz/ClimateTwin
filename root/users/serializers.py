
from . import models
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = models.BadRainbowzUser
        fields = ['id', 'username', 'password', 'email', 'phone_number', 'addresses'] 


class BadRainbowzUserSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.BadRainbowzUser
        fields = ['id', 'username', 'password', 'email', 'phone_number', 'addresses']




class TreasureSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.Treasure
        fields = "__all__"



class UserProfileSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.UserProfile
        fields = "__all__"


class UserSettingsSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.UserSettings
        fields = "__all__"


class UserVisitSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.UserVisit
        fields = "__all__"


class InboxSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.Inbox
        fields = "__all__"


        
class MessageSerializer(serializers.ModelSerializer):
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = models.Message
        fields = ['id', 'sender', 'recipient', 'content', 'timestamp', 'content_object']

    def get_content_object(self, obj):
        # Here, you can customize how the content_object is serialized
        if isinstance(obj.content_object, models.FriendRequest):
            return FriendRequestSerializer(obj.content_object).data
        # Handle other content_object types if needed
        if isinstance(obj.content_object, models.GiftRequest):
            return GiftRequestSerializer(obj.content_object).data
        return None


class FriendRequestSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.FriendRequest
        fields = "__all__"


class GiftRequestSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.GiftRequest
        fields = ['message', 'is_accepted', 'is_rejected', 'treasure', 'sender', 'recipient']

    def create(self, validated_data):
        # Remove 'sender' from validated data before creating the instance
        validated_data.pop('sender', None)
        return super().create(validated_data)


class FriendshipSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.Friendship
        fields = "__all__"

class FriendProfileSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.FriendProfile
        fields = "__all__"


class InboxItemSerializer(serializers.ModelSerializer):

    content_object = MessageSerializer()

    class Meta(object):
        model = models.InboxItem
        fields = "__all__"

        
        