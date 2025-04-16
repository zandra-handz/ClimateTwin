from datetime import datetime


def format_date(dt):
    current_year = datetime.now().year
    if dt.year == current_year:
        formatted_date = dt.strftime('%B %#d at %#I:%M %p')
    else:
        formatted_date = dt.strftime('%B %#d %Y at %#I:%M %p')

    return formatted_date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext as _
from .managers import CustomUserManager
from .utils import get_coordinates


# Create your models here.
class BadRainbowzUser(AbstractUser):

    # Username and email must be unique.
    username = models.CharField(_('username'), unique=True, max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    
    password_reset_code = models.CharField(max_length=6, blank=True, null=True)
    code_expires_at = models.DateTimeField(blank=True, null=True)

    addresses = models.JSONField(blank=True, null=True)
    phone_number = models.CharField(_('phone number'), max_length=15, blank=True, null=True)
    is_active_user = models.BooleanField(default=True)
    is_inactive_user = models.BooleanField(default=False)
    is_banned_user = models.BooleanField(default=False)
    is_test_user = models.BooleanField(default=False)

    is_subscribed_user = models.BooleanField(default=False)
    subscription_expiration_date = models.DateTimeField(null=True, blank=True)

    is_searchable = models.BooleanField(default=True)
    is_searchable_by_email = models.BooleanField(default=True)

    created_on = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(auto_now=True)

    app_setup_complete = models.BooleanField(default=False)

    last_login_at = models.DateTimeField(blank=True, null=True)
    login_attempts = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email',)  

    objects = CustomUserManager()

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username
    

    def generate_password_reset_code(self):
        import random
        from datetime import timedelta  # You can still use timedelta for durations
        
        code = f"{random.randint(100000, 999999)}"  # 6-digit code
        self.password_reset_code = code
        self.code_expires_at = timezone.now() + timedelta(minutes=10)  # Use timezone.now()
        self.save()
        return code
    
    
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

    def save(self, *args, **kwargs):
        created = not self.pk  # Check if the instance is being created
        super().save(*args, **kwargs)  # Call the original save method

        # If the instance is being created, create UserProfile and UserSettings
        if created:
            UserProfile.objects.create(user=self)
            UserSettings.objects.create(user=self)

    # def create_user_profile_and_settings(sender, instance, created, **kwargs):
    #     if created:
    #         UserProfile.objects.create(user=instance)
    #         UserSettings.objects.create(user=instance)


class UserSettings(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='settings')
    # not activated yet
    interests = models.JSONField(blank=True, null=True)
    receive_notifications = models.BooleanField(default=False)
    language_preference = models.CharField(max_length=10, choices=[('en', 'English'), ('es', 'Spanish')], blank=True)

    # Accessibility settings options for front end
    large_text = models.BooleanField(default=False)
    high_contrast_mode = models.BooleanField(default=False)
    screen_reader = models.BooleanField(default=False)

    manual_dark_mode = models.BooleanField(null=True, blank=True)
    expo_push_token = models.CharField(max_length=255, null=True, blank=True) 

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
    bio = models.CharField(max_length=3000, null=True, blank=True) 
    avatar = models.ImageField(upload_to='images/', blank=True, null=True)
    #gender = models.CharField(_('gender'), max_length=10, choices=[('NB', 'Non-Binary'), ('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('No answer', 'Uninterested in answering this')], blank=True, default='')

    def __str__(self):
        return f"Profile for {self.user.username}"


class Friendship(models.Model):
    initiator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='friendships_started')
    reciprocator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="friendships_accepted")
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        date = self.created_on 
        date = format_date(date)

        return f"Friendship formed between {self.initiator} and {self.reciprocator} on {date}"


class FriendProfile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='friend_of')
    nickname = models.CharField(max_length=255, default='')
    created_on = models.DateTimeField(default=timezone.now)
    friendship = models.ForeignKey(Friendship, on_delete=models.CASCADE, related_name="friendship")

    class Meta:
        ordering = ['-created_on']

        verbose_name = "User friendship"
        verbose_name_plural = "User friendships"

    def __str__(self):

        date = self.created_on 
        date = format_date(date)

        return f"{self.friend.username} ({self.nickname}) since {self.created_on}"


class UserVisit(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='visits')
    location_name = models.CharField(max_length=255)
    location_latitude = models.FloatField(default=0.0)
    location_longitude = models.FloatField(default=0.0)
    visit_created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_created_on']


    def __str__(self):

        date = self.visit_created_on
        date = format_date(date)

        return f"{self.user.username} visited {self.location_name} on {date}"



# may want to do something with treasures in the event current user deletes account
# abandon them somewhere or put them into some category where they randomly appear for other users to collect?
# we also may need to make a way to delete all associated treasures for legal purposes
# or state somewhere that they won't be able to be deleted easily once given away
# oooh give other users the ability to return any treasure back to the finder with a note
# are we storing the history of the treasure being exchanged?
class Treasure(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='treasures')
    finder = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,  # Set finder to NULL instead of deleting Treasure
        related_name='found_treasures',
        null=True, blank=True
    )
    original_user = models.CharField(max_length=50, default='')
    miles_traveled_to_collect = models.FloatField(default=0.0)
    location_name = models.CharField(max_length=255)
    found_at_latitude = models.FloatField(default=0.0)
    found_at_longitude = models.FloatField(default=0.0)
    descriptor = models.CharField(max_length=50, default="Mystery Item")  #type of item found, must be entered
    description = models.CharField(max_length=10000, null=True, blank=True) #description of item
    item_name = models.CharField(max_length=255, default='') #data item most associated with found item
    item_category = models.CharField(max_length=255, default='') #data item category

    add_data = models.JSONField(default=dict, null=True, blank=True)
    pending = models.BooleanField(default=False)

    # Gift-related fields
    message = models.TextField(null=True, blank=True)
    giver = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_gifts')
    giver_name = models.CharField(max_length=50, default='')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='received_gifts')
    created_on = models.DateTimeField(auto_now_add=True)
    owned_since = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-owned_since']


    def __str__(self):

        if self.owned_since:
            owned_since = self.owned_since
            owned_since = format_date(owned_since)
        else:
            owned_since = "No data"

        date_found = self.created_on
        date_found = format_date(date_found)

        if self.recipient:
            return f"Given a {self.descriptor} from {self.location_name} on {owned_since}"
        else:
            return f"Found {self.descriptor} in {self.location_name} on {date_found}"

    @classmethod
    def collect_item(cls, user, location_name, miles_traveled_to_collect, found_at_latitude, found_at_longitude, item_name, item_category, descriptor, description, add_data):
        
        return cls.objects.create(
            user=user,
            finder=user,
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

        username = self.user.username if self.user else "Unknown"

        self.giver = self.user
        self.giver_name = username
        self.user = recipient
        self.recipient = recipient 
        self.message = message
        self.owned_since = timezone.now() 
        self.pending = False
        self.save()

    def discard(self):
        self.delete()


class TreasureHistory(models.Model):
    treasure = models.OneToOneField(Treasure, on_delete=models.CASCADE, related_name='treasure_history')
    total_owners = models.PositiveIntegerField(default=1)
    times_gifted = models.PositiveIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

class TreasureOwnerChangeRecord(models.Model):
    treasure_history = models.ForeignKey(TreasureHistory, on_delete=models.CASCADE, related_name='owner_changes')
    treasure = models.ForeignKey(Treasure, on_delete=models.CASCADE, related_name='treasure_owner_changes')
    giver = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='treasure_given_record')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='treasure_received_record')
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
   


class Inbox(models.Model): # not in use, will probably be used for inbox settings.
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='inbox')
    items = GenericRelation('InboxItem')

    class Meta:
        verbose_name = "Inbox"
        verbose_name_plural = "Inboxes"

    def __str__(self):
        return f"Inbox for {self.user.username}"



class Message(models.Model):
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    
    # GenericForeignKey to associate any object with the message
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=1)
    object_id = models.PositiveIntegerField(default=1)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Is this set up yet?
    sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):

        date = self.timestamp 
        date = format_date(date)

        return f"Message {self.id} from {self.sender} to {self.recipient} on {date}"


class InboxItem(models.Model):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='inbox_items')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None, null=True, related_name='inbox_item_for_message')
    created_on = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):

        if self.message:
            sender = self.message.sender

            if self.message.content_object:# and self.message.content_object.special_type:
                message_type = self.message.content_object.special_type

            else:
                message_type = self.message.content_type
        else:
            message_type = "empty message"
            sender = "unknown sender"

        if self.is_read:
            read_status = "Read"
        else:
            read_status = "Unread"


        date = self.created_on 
        date = format_date(date)


        return f"{read_status} {message_type} from {sender}, sent on {date} (Id: {self.id})"

class FriendRequest(models.Model):
    special_type = models.CharField(max_length=50, default='friend request', editable=False)
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_friend_requests')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_friend_requests')
    message = models.TextField()
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    outer_message = GenericRelation(Message, null=True, default=None)

    class Meta:
        ordering = ['-created_on']

    def delete(self, *args, **kwargs):

        try:
            message = self.outer_message.get()
            message.delete()
        except Message.DoesNotExist:
            pass  

        super(FriendRequest, self).delete(*args, **kwargs)

    def __str__(self):
        return f"Friend request {self.id} from {self.sender.username} to {self.recipient.username}"
    


class GiftRequest(models.Model):
    special_type = models.CharField(max_length=50, default='gift request', editable=False)
    treasure = models.ForeignKey(Treasure, on_delete=models.CASCADE, related_name='request_to_gift')
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_gift_requests')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='received_gift_requests')
    message = models.TextField()
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    outer_message = GenericRelation(Message, null=True, default=None)

    class Meta:
        ordering = ['-created_on']

    def delete(self, *args, **kwargs):
        try:
            message = self.outer_message.get()
            message.delete()
        except Message.DoesNotExist:
            pass  

        super(GiftRequest, self).delete(*args, **kwargs)

    def __str__(self):
        return f"Gift request from {self.sender.username} to {self.recipient.username}"