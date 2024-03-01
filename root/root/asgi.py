# ASGI config

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from climatevisitor.consumers import AnimationConsumer
from climatevisitor.routing import websocket_urlpatterns # Correct import

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

# Get the Django ASGI application
django_asgi_app = get_asgi_application()

# Define the ProtocolTypeRouter for ASGI
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # For HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)  # Correct usage of routing
    ),  # For WebSocket requests
})
