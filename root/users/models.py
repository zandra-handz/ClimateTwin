from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from .managers import CustomUserManager
from .utils import get_coordinates

# Create your models here.
class BadRainbowzUser(AbstractUser):

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

    # Make username unique
    username = models.CharField(_('username'), unique=True, max_length=150)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email',)  # Swapped these two

    objects = CustomUserManager()

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username
    
    def add_address(self, address_data):
        """
        Add an address to the user's addresses if it is valid.
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
        Append a validated address to the user's addresses.
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

    # Accessibility settings
    large_text = models.BooleanField(default=False)
    high_contrast_mode = models.BooleanField(default=False)
    screen_reader = models.BooleanField(default=False)

    # Add other settings fields as needed

    def __str__(self):
        return f"Settings for {self.user.username}"



class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')
    
    # Additional fields related to user profile
    first_name = models.CharField(_('first name'), max_length=30, blank=True, default='')
    last_name = models.CharField(_('last name'), max_length=30, blank=True, default='')
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    #profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    gender = models.CharField(_('gender'), max_length=10, choices=[('NB', 'Non Binary'), ('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, default='')

    # Add other profile-related fields as needed

    def __str__(self):
        return f"Profile for {self.user.username}"



class UserVisit(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='visits')
    location_name = models.CharField(max_length=255)
    visit_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} visited {self.location_name} at {self.visit_datetime}"



class CollectedItem(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='collected_items')
    location_name = models.CharField(max_length=255)
    item_key = models.CharField(max_length=50)
    item_value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} collected {self.item_key} at {self.location_name}"