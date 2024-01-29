from django.contrib import admin
from .models import ClimateTwinLocation, ClimateTwinDiscoveryLocation

# Register your models here.
admin.site.register(ClimateTwinLocation)
admin.site.register(ClimateTwinDiscoveryLocation)