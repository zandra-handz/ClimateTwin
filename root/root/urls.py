"""
URL configuration for root project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from .api_info import info 
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from rest_framework_swagger.views import get_swagger_view 
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from climatevisitor import routing

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

#http://127.0.0.1:8000/#/activate/Nw/c1f76q-af6408c556d882b5de0aee38033ee102
schema_view = get_schema_view((info), public=True,
    permission_classes=(permissions.AllowAny,))


urlpatterns = [
    
    re_path(r'^doc(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),  #<-- Here
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), 

    path('ws/', URLRouter(routing.websocket_urlpatterns)),

    path('admin/', admin.site.urls),
    path('climatevisitor/', include('climatevisitor.urls')),
    
    # Djoser URLs
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.urls.authtoken')),
    
    # Allauth URLs
    path('all-auth/', include('allauth.urls')),
    path('users/', include('users.urls')),

    path('users/token/', TokenObtainPairView.as_view(), name='get_token'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),

    
]
