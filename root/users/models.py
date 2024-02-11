from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from .managers import CustomUserManager
from .utils import get_coordinates


# Create your models here.
class BadRainbowzUser(AbstractUser):

    # Username and email must be unique.
    username = models.CharField(_('username'), unique=True, max_length=150)
    email = models.EmailField(_('email address'), unique=True)

    addresses = models.JSONField(blank=True, null=True)
    phone_number = models.CharField(_('phone number'), max_length=15, blank=True, null=True)
    is_active_user = models.BooleanField(default=True)
    is_inactive_user = models.BooleanField(default=False)
    is_banned_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    login_attempts = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email',)  

    objects = CustomUserManager()

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username
    
    def add_address(self, address_data):
        """
        Add address if valid.
        """
        address_value = address_data[0]['address']
        coordinates = get_coordinates(address_value)

        if coordinates:
            if 'addresses' not in self.__dict__:
                self.addresses = []
            
            new_address_entry = {
                'nickname': address_data[0]['nickname'],
                'address': address_value,
                'coordinates': coordinates
            }

            self.addresses.append(new_address_entry)
            self.save()
            return True
        return False

    
    def add_validated_address(self, nickname, address, coordinates):
        """
        Append validated address to addresses list.
        """
        if 'addresses' not in self.__dict__:
            self.addresses = []

        new_address_entry = {
            'nickname': nickname,
            'address': address,
            'coordinates': coordinates
        }

        self.addresses.append(new_address_entry)
        self.save()


class UserSettings(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='settings')
    receive_notifications = models.BooleanField(default=False)
    language_preference = models.CharField(max_length=10, choices=[('en', 'English'), ('es', 'Spanish')], blank=True)

    # Accessibility settings.
    large_text = models.BooleanField(default=False)
    high_contrast_mode = models.BooleanField(default=False)
    screen_reader = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User settings"
        verbose_name_plural = "User settings"

    def __str__(self):
        return f"Settings for {self.user.username}"



class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(_('first name'), max_length=30, blank=True, default='')
    last_name = models.CharField(_('last name'), max_length=30, blank=True, default='')
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    #profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    gender = models.CharField(_('gender'), max_length=10, choices=[('NB', 'Non-Binary'), ('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('No answer', 'Uninterested in answering this')], blank=True, default='')

    def __str__(self):
        return f"Profile for {self.user.username}"



class UserFriendship(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='friend_of')
    nickname = models.CharField(max_length=255, default='')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "User friendship"
        verbose_name_plural = "User friendships"

    def __str__(self):
        return f"{self.user.username} - {self.friend.username} ({self.nickname})"



class UserVisit(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='visits')
    location_name = models.CharField(max_length=255)
    location_latitude = models.FloatField(default=0.0)
    location_longitude = models.FloatField(default=0.0)
    visit_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} visited {self.location_name} at {self.visit_datetime}"



class Treasure(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='treasures')
    original_user = models.CharField(max_length=50, default='')
    miles_traveled_to_collect = models.FloatField(default=0.0)
    location_name = models.CharField(max_length=255)
    found_at_latitude = models.FloatField(default=0.0)
    found_at_longitude = models.FloatField(default=0.0)
    descriptor = models.CharField(max_length=50, default="Mystery Item")  #type of item found, must be entered
    description = models.CharField(max_length=600, null=True, blank=True) #description of item
    item_name = models.CharField(max_length=255, default='') #data item most associated with found item
    item_category = models.CharField(max_length=255, default='') #data item category

    add_data = models.JSONField(default=dict, null=True, blank=True)
    pending = models.BooleanField(default=False)

    # Gift-related fields.
    message = models.TextField(null=True, blank=True)
    giver = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name='sent_gifts')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name='received_gifts')
    created_on = models.DateTimeField(auto_now_add=True)
    owned_since = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self.recipient:
            return f"Gifted {self.descriptor} from {self.location_name} to {self.recipient.username} on {self.owned_since}"
        else:
            return f"Collected {self.descriptor} from {self.location_name} by {self.user.username} on {self.created_on}"

    @classmethod
    def collect_item(cls, user, location_name, miles_traveled_to_collect, found_at_latitude, found_at_longitude, item_name, item_category, descriptor, description, add_data):
        
        return cls.objects.create(
            user=user,
            original_user=user,
            location_name=location_name,
            miles_traveled_to_collect=miles_traveled_to_collect,
            found_at_latitude=found_at_latitude,
            found_at_longitude=found_at_longitude,
            item_name=item_name,
            item_category=item_category,
            descriptor=descriptor,
            description=description,
            add_data=add_data
        )

    def give_as_gift(self, message, giver, recipient):
        # Update the fields for gifting (not in use right now).
        self.message = message
        self.giver = giver
        self.recipient = recipient
        self.pending = True
        self.save()

    def accept(self, message, recipient):
        self.giver = self.user
        self.user = recipient
        self.recipient = recipient 
        self.message = message
        self.owned_since = timezone.now() 
        self.pending = False
        self.save()

    def discard(self):
        self.delete()

    

class Inbox(models.Model): # not in use, will probably be used for inbox settings.
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='inbox')
    items = GenericRelation('Item')

    class Meta:
        verbose_name = "Inbox"
        verbose_name_plural = "Inboxes"

    def __str__(self):
        return f"Inbox for {self.user.username}"


class Item(models.Model):  # change name to InboxItem.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    reverse_relation = GenericRelation('Item')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inbox Item ({self.content_type}): {self.content_object}"


class Message(models.Model):
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # GenericForeignKey to associate any object with the message.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=1)
    object_id = models.PositiveIntegerField(default=1)
    content_object = GenericForeignKey('content_type', 'object_id')

    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"


class FriendRequest(models.Model):
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_friend_requests')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_friend_requests')
    message = models.TextField()
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Friend request from {self.sender.username} to {self.recipient.username}"


class GiftRequest(models.Model):
    treasure = models.ForeignKey(Treasure, on_delete=models.CASCADE, related_name='request_to_gift')
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_gift_requests')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_gift_requests')
    message = models.TextField()
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gift request from {self.sender.username} to {self.recipient.username}"