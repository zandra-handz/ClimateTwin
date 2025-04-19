from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', views.index, name='index'),
    #path('endpoints/', views.endpoints, name='endpoints'),
    path('demo/', views.demo, name='demo'),

    # Play the game
    path('go/', views.go, name='go'),
    path('get-remaining-goes/', views.get_remaining_goes, name='get-remaining-goes'),
    path('launchpad-data/', views.MostRecentHomeLocationView.as_view(), name='most-recent-home-location'),
    path('currently-visiting/', views.CurrentTwinLocationView.as_view(), name='currently-visiting-location'),
    path('currently-nearby/', views.CurrentDiscoveryLocationsView.as_view(), name='current-nearby-locations'),
    path('explore/', views.CreateExploreLocationView.as_view(), name='create-explore-location'),
    path('explore/v2/', views.CreateOrUpdateCurrentLocationView.as_view(), name='create-or-update-current-location'),
    
    path('currently-exploring/', views.CurrentExploreLocationView.as_view(), name='currently-exploring'),
    path('currently-exploring/v2/', views.CurrentLocationView.as_view(), name='currently-exploring-v2'),
   
    path('collect/', views.collect, name='collect-treasure'),
    path('item-choices/', views.item_choices, name="item-choices"),

    path('go-home/', views.ExpireCurrentLocationView.as_view(), name='expire-current-location'),

    path('algo-stats-for-user/', views.ClimateTwinSearchStatsView.as_view(), name='algo-stats-for-user'),
    

    # Access all data associated with user
    path('locations/home/', views.HomeLocationsView.as_view(), name='home-locations'),
    path('locations/home/<int:pk>/', views.HomeLocationView.as_view(), name='home-location'),
    path('locations/twins/', views.TwinLocationsView.as_view(), name='twin-locations'),
    path('locations/twin/<int:pk>/', views.TwinLocationView.as_view(), name='twin-location'),
    path('locations/nearby/', views.DiscoveryLocationsView.as_view(), name='ancient-ruins-found'),
    path('locations/nearby/<int:pk>/', views.DiscoveryLocationView.as_view(), {'delete': 'destroy'}, name='delete-discovery-location'),
    path('locations/explored/', views.ExploreLocationsView.as_view(), name='explored-locations'),
    path('explore-location/<int:pk>/', views.ExploreLocationView.as_view(), name='explored-location'),

    # View data related to algorithm performance
    path('performance/compare/full-locations/', views.MatchPerformanceView.as_view(), name='compare-locations'),
    path('performance/compare/full-locations/current/', views.CurrentLocationMatchView.as_view(), name='compare-current-location'),
    path('performance/compare/key-data/', views.key_data, name='compare-key-data'),

    path('api-token-auth/', obtain_auth_token),


    path('clean-discoveries-data/', views.clean_old_discoveries_locations, name='clean_discoveries_data'),   
    
]
 
 