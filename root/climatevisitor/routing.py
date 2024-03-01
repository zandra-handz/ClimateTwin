# routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from climatevisitor.consumers import AnimationConsumer
from climatevisitor.consumer import ClimateTwinConsumer

websocket_urlpatterns = [
    path('animation/', AnimationConsumer.as_asgi()),
    re_path(r'ws/climate-twin/$', ClimateTwinConsumer.as_asgi()),
]
