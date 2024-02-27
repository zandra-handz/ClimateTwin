# tasks.py
from celery import shared_task

@shared_task
def send_coordinate_update(latitude, longitude):
    print(f"Sending update for coordinate pair: {latitude}, {longitude}")
