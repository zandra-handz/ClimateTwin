# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import logging 

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import requests

from climatevisitor.tasks.tasks import send_current_location_to_celery

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

app = Celery(
    'root'
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name='algorithms_task')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name='algorithms')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, run_current_location_task.s(), name='send_current_location')



@app.task
def run_current_location_task()
    send_current_location_to_celery()


'''
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'location_update',
        {
            'type': 'current_location',
            'name': 'hiiii',
            'latitude': 'hiiii',
            'longitude': 'hiiii',
        }
    )
    
'''

'''
# Use the REDIS_URL from Django settings for the broker and backend
#app.conf.broker_url = 'redis://default:AVNS_TKxUs1XBH-EKD3Nw47P@db-redis-climatetwin-do-user-15838008-0.c.db.ondigitalocean.com:25061'
app.conf.broker_url = settings.REDIS_URL
app.conf.result_backend = settings.REDIS_URL

# Load settings from Django settings file
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks
app.autodiscover_tasks()
'''

'''
local
app = Celery('root')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
'''

'''
digital ocean  
app = Celery("yourapp")
app.conf.broker_url = os.environ.get("REDIS_URL", "redis://localhost:6379") 



# Stackoverflow 
app = Celery(
    'root',
    broker_use_ssl={'ssl_cert_reqs': CERT_NONE},
    redis_backend_use_ssl={'ssl_cert_reqs': CERT_NONE}
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
# End stackoverflow
'''