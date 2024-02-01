from django.contrib import admin
from .models import ClimateTwinLocation, ClimateTwinDiscoveryLocation, ClimateTwinExploreDiscoveryLocation

# Register your models here.
admin.site.register(ClimateTwinLocation)
admin.site.register(ClimateTwinDiscoveryLocation)
admin.site.register(ClimateTwinExploreDiscoveryLocation)