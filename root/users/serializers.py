
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
            # Serialize the GiftRequest object
            gift_request_data = GiftRequestSerializer(obj.content_object).data
            # Include the associated Treasure data
            treasure_data = {
                'treasure_descriptor': obj.content_object.treasure.descriptor,
                'treasure_description': obj.content_object.treasure.description
            }
            # Merge the GiftRequest data with the Treasure data
            gift_request_data.update(treasure_data)
            return gift_request_data
        return None


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.FriendRequest
        fields = ['id', 'special_type', 'sender', 'message','recipient']
        read_only_fields = ['id']

    def create(self, validated_data):
        # Automatically set sender field to current user
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        # Perform additional validation here if needed
        return data


class GiftRequestSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    treasure = serializers.PrimaryKeyRelatedField(queryset=models.Treasure.objects.all(), write_only=True)

    class Meta:
        model = models.GiftRequest
        fields = ['id', 'special_type', 'sender', 'message', 'treasure', 'recipient']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        # Perform additional validation here if needed
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

    class Meta(object):
        model = models.InboxItem
        fields = "__all__"

        
        