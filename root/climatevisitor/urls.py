from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', views.index, name='index'),
    path('endpoints/', views.endpoints, name='endpoints'),
    path("go/", views.go, name="go"),
    path("collect/", views.collect, name="collect"),
    path("item-choices/", views.item_choices, name="item-choices"),
    path('visited/', views.ClimateTwinLocationsView.as_view(), name='visited-locations'),
    path('visited/<int:pk>', views.ClimateTwinLocationView.as_view(), name='visited-location'),
    path('currently-visiting/', views.CurrentClimateTwinLocationView.as_view(), name='current-visiting-location'),
    path('found/', views.ClimateTwinDiscoveryLocationsView.as_view(), name='ancient-ruins-found'),
    path('found/<int:pk>', views.ClimateTwinDiscoveryLocationView.as_view(), {'delete': 'destroy'}, name='delete-discovery-location'),
    path('currently-nearby/', views.CurrentClimateTwinDiscoveryLocationsView.as_view(), name="current-nearby-locations"),
    path('explored/', views.ClimateTwinExploreDiscoveryLocationsView.as_view(), name='explored-locations'),
    path('explored/<int:pk>', views.ClimateTwinExploreDiscoveryLocationView.as_view(), name='explored-location'),
    path('currently-exploring/', views.CurrentClimateTwinExploreDiscoverLocationView.as_view(), name="currently-exploring"),
    path('api-token-auth/', obtain_auth_token)
]
 