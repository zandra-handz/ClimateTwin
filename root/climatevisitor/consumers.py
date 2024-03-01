import logging
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import sync_to_async
from .tasks import send_coordinate_update_to_celery

logger = logging.getLogger(__name__)

class AnimationConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        logger.info("WebSocket connection established.")

    async def receive(self, text_data):
        latitude = 123.456  # Replace with actual latitude value
        longitude = 789.012  # Replace with actual longitude value
        logger.info("Received message: %s", text_data)
        await self.send_coordinate_update_async(latitude, longitude)

    def disconnect(self, close_code):
        logger.info("WebSocket connection closed.")

    @sync_to_async
    def send_coordinate_update_async(self, latitude, longitude):
        return send_coordinate_update_to_celery.delay(latitude, longitude)
