from django.contrib import admin
from .models import BadRainbowzUser, ItemInbox, Treasure, UserProfile, UserSettings, UserVisit

# Register your models here.
admin.site.register(BadRainbowzUser)
admin.site.register(ItemInbox)
admin.site.register(Treasure)
admin.site.register(UserSettings)
admin.site.register(UserProfile)
admin.site.register(UserVisit)

