from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.BadRainbowzUser)
admin.site.register(models.FriendRequest)
admin.site.register(models.GiftRequest)
admin.site.register(models.Inbox)
admin.site.register(models.InboxItem)
admin.site.register(models.Message)
admin.site.register(models.Treasure) 
admin.site.register(models.TreasureHistory)
admin.site.register(models.TreasureOwnerChangeRecord)
admin.site.register(models.Friendship)
admin.site.register(models.FriendProfile)
admin.site.register(models.UserSettings)
admin.site.register(models.UserProfile)
admin.site.register(models.UserVisit)

