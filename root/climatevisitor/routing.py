# routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from climatevisitor.consumers import AnimationConsumer
from climatevisitor.consumer import ClimateTwinConsumer, LocationUpdateConsumer
from climatevisitor.middleware import TokenAuthMiddlewareStack

websocket_urlpatterns = [
    path('animation/', AnimationConsumer.as_asgi()),
    re_path(r'ws/climate-twin/$', ClimateTwinConsumer.as_asgi()),
    re_path(r'ws/climate-twin/current/$', LocationUpdateConsumer.as_asgi()),
]


application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})


'''

Stackoverflow:

from <app-name>.consumers import <consumer-name>

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter([
            path('<route>/', <consumer-name>),
        ]),
    ),
})

'''