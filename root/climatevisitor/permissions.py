# climatevisitor.permissions.py 

# Not currently in use (for practice only)

from rest_framework import permissions


class AdminOrReadOnly(permissions.IsAdminUser):

    def has_permission(self, request, view):
        admin_permission = bool(request.user and request.user.is_staff) 
        return request.method == "GET" or admin_permission


class ReviewUserOrReadOnly(permissions.BasePermission):

    def has_object_permssion(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True  
        else:
            return obj.review_user == request.user


# in views.py:
# from climatevisitor.permissions import AdminOrReadOnly, ReviewUserOrReadOnly

# permission_classes = [AdminOrReadOnly]
# permission_classes = [ReviewUserOrReadOnly]