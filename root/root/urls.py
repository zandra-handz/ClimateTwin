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
from django.contrib import admin
from django.urls import path, include
#http://127.0.0.1:8000/#/activate/Nw/c1f76q-af6408c556d882b5de0aee38033ee102
urlpatterns = [
    path('admin/', admin.site.urls),
    path('climatevisitor/', include('climatevisitor.urls')),
    path('climatevisitor/visited/', include('climatevisitor.urls')),
    
    # Djoser URLs
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    
    # Allauth URLs
    path('auth/', include('allauth.urls')),
    path('users/', include('users.urls')),
]