from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('', views.index, name='index'),
    path('endpoints/', views.endpoints, name='endpoints'),
    path('api-token-auth/', obtain_auth_token),
    path("go/", views.go, name="go"),
    path("collect/", views.collect, name="collect"),
    path("item-choices/", views.item_choices, name="item-choices"),
    path('visited/', views.ClimateTwinLocationsView.as_view(), name='visited-locations'),
    path('visited/<int:pk>', views.ClimateTwinLocationView.as_view(), name='visited-location'),
    #path('visited/viewset/', views.ClimateTwinLocationViewSet.as_view({'get':'list'})),
    path('found/', views.ClimateTwinDiscoveryLocationsView.as_view(), name='ancient-ruins-found'),
    path('found/<int:pk>', views.ClimateTwinDiscoveryLocationView.as_view(), name='ancient-ruin-found'),
    #path('found/viewset/', views.ClimateTwinDiscoveryLocationViewSet.as_view({'get':'list'})),
    path('exploring/', views.ClimateTwinExploreDiscoveryLocationsView.as_view(), name='exploring'),
    path('exploring/<int:pk>', views.ClimateTwinExploreDiscoveryLocationView.as_view(), name='exploring'),
    #path('exploring/viewset/', views.ClimateTwinExploreDiscoveryLocationViewSet.as_view({'get':'list'}))
]
 