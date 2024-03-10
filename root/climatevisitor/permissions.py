# climatevisitor.permissions.py 

# Not currently in use (for practice only)

from rest_framework import permissions


class AdminOrReadOnly(permissions.IsAdminUser):
    pass