from . import models
from django.contrib import admin
# Register your models here.
admin.site.register(models.HomeLocation)
admin.site.register(models.ClimateTwinLocation)

admin.site.register(models.ClimateTwinDiscoveryLocation)

admin.site.register(models.ClimateTwinExploreLocation)

admin.site.register(models.CurrentLocation)