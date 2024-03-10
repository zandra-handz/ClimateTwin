import os
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from climatevisitor.consumers import AnimationConsumer
from climatevisitor.routing import websocket_urlpatterns # Correct import
from root.middleware import TokenAuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')


django_asgi_app = get_asgi_application()


logger = logging.getLogger(__name__)

# Define a function to log request headers
async def log_request_headers(scope, receive, send):
    if scope['type'] == 'http':
        logger.debug("Incoming HTTP request headers: %s", scope.get('headers', []))
    return await django_asgi_app(scope, receive, send)

# Define the ProtocolTypeRouter for ASGI
application = ProtocolTypeRouter({
    #"http": log_request_headers,
    #"websocket": AuthMiddlewareStack(
    #    URLRouter(websocket_urlpatterns)  # Correct usage of routing
   # ),
#})
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})