
from . import models
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers


class StrLinkSerializer(serializers.Serializer):
    def __init__(self, view_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['str'] = serializers.StringRelatedField(source='__str__')
        self.fields['hyperlink'] = serializers.HyperlinkedIdentityField(
            view_name=view_name,
            read_only=True
        )




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
    inbox_item_message = StrLinkSerializer

    class Meta:
        model = models.Message
        fields = ['id', 'sender', 'recipient', 'content', 'created_on', 'content_object']

    def get_content_object(self, obj):
        
        if isinstance(obj.content_object, models.FriendRequest):
            return FriendRequestSerializer(obj.content_object).data
      
        if isinstance(obj.content_object, models.GiftRequest):
            
            gift_request_data = GiftRequestSerializer(obj.content_object).data
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
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
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


class AcceptRejectFriendRequestSerializer(serializers.ModelSerializer):
    message = serializers.HiddenField(default="Your message here")

    class Meta:
        model = models.FriendRequest
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

class UserSummarySerializer(serializers.ModelSerializer):

    friends = serializers.StringRelatedField(many=True)
    treasures = serializers.StringRelatedField(many=True)
    visits = serializers.StringRelatedField(many=True)
    inbox_items = serializers.StringRelatedField(many=True)


    class Meta(object):

        model = models.BadRainbowzUser
        # Limit info for demo purposes
        exclude = ['password', 'is_superuser', 'is_staff', 'username', 'email']


class UserLinksSerializer(serializers.ModelSerializer):

    friends = StrLinkSerializer(view_name='friend', many=True)
    treasures = StrLinkSerializer(view_name='treasure', many=True)
    visits = StrLinkSerializer(view_name='visited-place', many=True)
    inbox_items = StrLinkSerializer(view_name='inbox-item-detail', many=True)


    class Meta(object):

        model = models.BadRainbowzUser
        exclude = ['password', 'is_superuser', 'is_staff', 'username', 'email']