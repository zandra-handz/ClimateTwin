import os
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path 
from climatevisitor.routing import application as websocket_application  # Import your WebSocket routing application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')


django_asgi_app = get_asgi_application() 

# Define the ProtocolTypeRouter for ASGI
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": websocket_application,
})



'''
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

'''