from django.urls import path
from .views import ActivateUser

urlpatterns = [

    path('activate/<uid>/<token>', ActivateUser.as_view({'get': 'activation'}), name='activation'),

] 