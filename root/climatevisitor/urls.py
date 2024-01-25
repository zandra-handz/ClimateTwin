from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', views.index, name='index'),
    path('api-token-auth/', obtain_auth_token),
    path('visited/', views.ClimateTwinLocationsView.as_view(), name='visited-locations'),
    path('visited/<int:pk>', views.ClimateTwinLocationView.as_view(), name='visited-location'),
    path('visited/viewset/', views.ClimateTwinLocationViewSet.as_view({'get':'list'}))
]
 