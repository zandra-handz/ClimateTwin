from django.contrib import admin
from .models import BadRainbowzUser, UserProfile, UserSettings, UserVisit, CollectedItem

# Register your models here.
admin.site.register(BadRainbowzUser)
admin.site.register(UserSettings)
admin.site.register(UserProfile)
admin.site.register(UserVisit)
admin.site.register(CollectedItem)
