# climatevisitor.permissions.py 

# Not currently in use (for practice only)

from rest_framework import permissions


class AdminOrReadOnly(permissions.IsAdminUser):

    def has_permission(self, request, view):
        admin_permission = bool(request.user and request.user.is_staff) 
        return request.method == "GET" or admin_permission



# in views.py:
# from climatevisitor.permissions import AdminOrReadOnly

# permission_classes = [AdminOrReadOnly]