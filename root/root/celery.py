# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import logging
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

app.conf.beat_schedule = {
    'fetch-current-location-every-minute': {
        'task': send_current_location_to_celery,
        'schedule': crontab(second='*/20'),
    },
}

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