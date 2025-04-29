
from . import models
from djoser.serializers import UserCreateSerializer
from django.core.exceptions import ValidationError
from rest_framework import serializers

from django.utils.timezone import now

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


# class BadRainbowzUserSerializer(serializers.ModelSerializer):

#     class Meta(object):
#         model = models.BadRainbowzUser
#         fields = ['id', 'username', 'password', 'email', 'phone_number', 'addresses']



class TreasureSearchableSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta(object):
        model = models.Treasure
        fields = "__all__"




class TreasureSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.Treasure
        fields = "__all__"


# Decided to just associate the logs with the treasure and not a treasure history model too
# class TreasureHistorySerializer(serializers.ModelSerializer):

#     class Meta(object):
#         model = models.TreasureHistory
#         fields = "__all__"


class TreasureOwnerChangeRecordSerializer(serializers.ModelSerializer):
    giver_username = serializers.CharField(source='giver.username', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)

    class Meta(object):
        model = models.TreasureOwnerChangeRecord
        fields = "__all__"

# class UserProfileSerializer(serializers.ModelSerializer):

#     class Meta(object):
#         model = models.UserProfile
#         fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    created_on = serializers.CharField(source='user.created_on', read_only=True)
    most_recent_visit = serializers.SerializerMethodField()
    total_visits = serializers.SerializerMethodField()

    # Override the avatar image field to return HTTPS URLs (taken from HellofriendFS code)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = models.UserProfile
        fields = "__all__"   

    def get_avatar(self, obj):

        if not obj.avatar:  
            return None
        
        try:
            avatar_url = obj.avatar.url   
        except ValueError:  
            return None
        
        # Ensure the URL uses HTTPS
        if avatar_url.startswith('http://'):
            avatar_url = avatar_url.replace('http://', 'https://')

        return avatar_url


    def get_most_recent_visit(self, obj):
        """Returns the most recent visit for the user"""
        recent_visit = obj.user.visits.first()  
        if recent_visit:
            return {
                "location_name": recent_visit.location_name,
                "latitude": recent_visit.location_latitude,
                "longitude": recent_visit.location_longitude,
                "visited_on": recent_visit.visit_created_on
            }
        return None  

    def get_total_visits(self, obj): 
        return obj.user.visits.count()
    
class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = '__all__'


class UserSettingsSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.UserSettings
        fields = "__all__"


class UserSharedDataSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.UserSharedData
        fields = "__all__"

class BadRainbowzUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    settings = UserSettingsSerializer(required=False)
    shared_data = UserSharedDataSerializer(required=False)

    class Meta:
        model = models.BadRainbowzUser 
        fields = ['id', 'created_on', 'password', 'is_banned_user', 'is_subscribed_user', 'is_superuser', 'subscription_expiration_date', 'username', 'email', 'app_setup_complete', 'is_test_user', 'phone_number', 'addresses', 'profile', 'settings', 'shared_data']
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        settings_data = validated_data.pop('settings', {})
        shared_data_data = validated_data.pop('shared_data', {})
        user = models.BadRainbowzUser.objects.create_user(**validated_data)
        if profile_data:
            models.UserProfile.objects.create(user=user, **profile_data)
        if settings_data:
            models.UserSettings.objects.create(user=user, **settings_data)
        if shared_data_data:
            models.UserSharedData.objects.create(user=user, **settings_data)
        return user

class PasswordResetCodeValidationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        reset_code = data['reset_code']

        try:
            user = models.BadRainbowzUser.objects.get(email=email)
        except models.BadRainbowzUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email or reset code.")
 
        if user.password_reset_code != reset_code:
            raise serializers.ValidationError("Invalid reset code.")
        if not user.code_expires_at or user.code_expires_at < now():
            raise serializers.ValidationError("Reset code has expired.")

        return data
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField()

    def validate(self, data):
        email = data['email']
        reset_code = data['reset_code']

        try:
            user = models.BadRainbowzUser.objects.get(email=email)
        except models.BadRainbowzUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email or reset code.")

        # Check if the code is correct and not expired
        if user.password_reset_code != reset_code:
            raise serializers.ValidationError("Invalid reset code.")
        if not user.code_expires_at or user.code_expires_at < now():
            raise serializers.ValidationError("Reset code has expired.")

        return user

    def save(self, user, new_password):
        user.set_password(new_password)
        user.password_reset_code = None  # Clear the reset code
        user.code_expires_at = None
        user.save()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise ValidationError("New password must be at least 8 characters long.")
        return value
    
    




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


class FriendRequestWithAddedDataSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    sender_avatar = serializers.SerializerMethodField(read_only=True)
    recipient_avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.FriendRequest
        fields = [
            'id', 'special_type', 'sender', 'message', 'recipient',
            'sender_username', 'sender_avatar',
            'recipient_username', 'recipient_avatar'
        ]
        read_only_fields = ['id']
    
    def get_sender_avatar(self, obj):
        avatar = getattr(obj.sender.profile, 'avatar', None)
        if not avatar:
            return None
        try:
            url = avatar.url
        except ValueError:
            return None
        return url.replace('http://', 'https://') if url.startswith('http://') else url

    def get_recipient_avatar(self, obj):
        avatar = getattr(obj.recipient.profile, 'avatar', None)
        if not avatar:
            return None
        try:
            url = avatar.url
        except ValueError:
            return None
        return url.replace('http://', 'https://') if url.startswith('http://') else url


    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        return data



class GiftRequestWithAddedDataSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True) 
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    sender_avatar = serializers.SerializerMethodField(read_only=True)
    recipient_avatar = serializers.SerializerMethodField(read_only=True)

    treasure = serializers.PrimaryKeyRelatedField(queryset=models.Treasure.objects.all(), write_only=True)
    treasure_data = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.GiftRequest
        fields = [
            'id', 'special_type', 'sender', 'message', 'treasure', 'treasure_data', 'recipient',
            'sender_username', 'sender_avatar',
            'recipient_username', 'recipient_avatar'
        ]
        read_only_fields = ['id']

    def get_treasure_data(self, obj): 
        return TreasureSerializer(obj.treasure).data
    

    def get_sender_avatar(self, obj):
        avatar = getattr(obj.sender.profile, 'avatar', None)
        if not avatar:
            return None
        try:
            url = avatar.url
        except ValueError:
            return None
        return url.replace('http://', 'https://') if url.startswith('http://') else url

    def get_recipient_avatar(self, obj):
        avatar = getattr(obj.recipient.profile, 'avatar', None)
        if not avatar:
            return None
        try:
            url = avatar.url
        except ValueError:
            return None
        return url.replace('http://', 'https://') if url.startswith('http://') else url


    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        # Perform additional validation here if needed
        return data

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.FriendRequest
        fields = ['id', 'special_type', 'sender', 'message', 'recipient']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        return data



class GiftRequestSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    #sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
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
    

class GiftRequestBackToFinderSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    #sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    treasure = serializers.PrimaryKeyRelatedField(queryset=models.Treasure.objects.all(), write_only=True)

    # Removed recipient from the fields
    class Meta:
        model = models.GiftRequest
        fields = ['id', 'special_type', 'sender', 'message', 'treasure', 'recipient']
        read_only_fields = ['id']

    def create(self, validated_data):
        # Allow the view to set the recipient, which is handled in the view
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        # Additional validation can go here if needed
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

# class FriendProfileSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source='friend.username', read_only=True)


#     class Meta(object):
#         model = models.FriendProfile
#         fields = "__all__"


class FriendProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='friend.username', read_only=True)
    friend_profile = UserProfileSerializer(source='friend.profile', read_only=True) 

    class Meta:
        model = models.FriendProfile
        fields = "__all__"



class InboxItemSerializer(serializers.ModelSerializer):
    display_text = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = models.InboxItem
        fields = "__all__"  
        extra_kwargs = {
            'display_text': {'read_only': True},
            'sender': {'read_only': True},
            'content_type': {'read_only': True}
        }

    def get_display_text(self, obj):
        return str(obj)  
     
    def get_sender(self, obj):
        if obj.message and obj.message.sender:
            sender = obj.message.sender
            return {
                "id": sender.id,
                "username": sender.username
            }
        return {"id": None, "username": "unknown sender"}
    
        
    def get_content_type(self, obj):
        if obj.message and obj.message.content_type:
            return str(obj.message.content_type)
        return "no content type"


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