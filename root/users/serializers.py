
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
        fields = ['special_type', 'sender', 'message', 'treasure', 'recipient']

    def create(self, validated_data):
        # Automatically set the sender field to the current user
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        # Perform additional validation if needed
        return data
    


class AcceptRejectGiftRequestSerializer(serializers.ModelSerializer):
    message = serializers.HiddenField(default="Your message here")

    class Meta:
        model = models.GiftRequest
        fields = ['is_accepted', 'is_rejected', 'message']

    def validate(self, data):
        return data



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

        
        