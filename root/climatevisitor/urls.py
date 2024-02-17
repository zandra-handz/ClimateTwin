from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', views.index, name='index'),
    path('endpoints/', views.endpoints, name='endpoints'),
    path('go/', views.go, name='go'),
    path('currently-visiting/', views.CurrentClimateTwinLocationView.as_view(), name='currently-visiting-location'),
    path('currently-nearby/', views.CurrentClimateTwinDiscoveryLocationsView.as_view(), name='current-nearby-locations'),
    path('explore/', views.ClimateTwinExploreDiscoveryLocationsView.as_view(method='post'), name='choose-new-explore-location'),
    path('currently-exploring/', views.CurrentClimateTwinExploreDiscoverLocationView.as_view(), name='currently-exploring'),
    path('collect/', views.collect, name='collect-treasure'),
    path('item-choices/', views.item_choices, name="item-choices"),
    path('locations/twins', views.ClimateTwinLocationsView.as_view(), name='twin-locations'),
    path('locations/twin/<int:pk>', views.ClimateTwinLocationView.as_view(), name='twin-location'),
    path('locations/nearby/', views.ClimateTwinDiscoveryLocationsView.as_view(), name='ancient-ruins-found'),
    path('locations/nearby<int:pk>', views.ClimateTwinDiscoveryLocationView.as_view(), {'delete': 'destroy'}, name='delete-discovery-location'),
    path('locations/explore/', views.ClimateTwinExploreDiscoveryLocationsView.as_view(method='get'), name='explored-locations'),
    path('explore-location/<int:pk>', views.ClimateTwinExploreDiscoveryLocationView.as_view(), name='explored-location'),
    path('api-token-auth/', obtain_auth_token)
]
 