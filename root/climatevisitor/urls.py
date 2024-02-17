from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', views.index, name='index'),
    path('endpoints/', views.endpoints, name='endpoints'),

    # Play the game
    path('go/', views.go, name='go'),
    path('currently-visiting/', views.CurrentTwinLocationView.as_view(), name='currently-visiting-location'),
    path('currently-nearby/', views.CurrentDiscoveryLocationsView.as_view(), name='current-nearby-locations'),
    path('explore/', views.CreateExploreLocationView.as_view(), name='create-explore-location'),
    path('currently-exploring/', views.CurrentExploreLocationView.as_view(), name='currently-exploring'),
    path('collect/', views.collect, name='collect-treasure'),
    path('item-choices/', views.item_choices, name="item-choices"),

    # Access all data associated with user
    path('locations/twins', views.TwinLocationsView.as_view(), name='twin-locations'),
    path('locations/twin/<int:pk>', views.TwinLocationView.as_view(), name='twin-location'),
    path('locations/nearby/', views.DiscoveryLocationsView.as_view(), name='ancient-ruins-found'),
    path('locations/nearby<int:pk>', views.DiscoveryLocationView.as_view(), {'delete': 'destroy'}, name='delete-discovery-location'),
    path('locations/explore/', views.ExploreLocationsView.as_view(), name='explored-locations'),
    path('explore-location/<int:pk>', views.ExploreLocationView.as_view(), name='explored-location'),

    path('api-token-auth/', obtain_auth_token)
]
 
 