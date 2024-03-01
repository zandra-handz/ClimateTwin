# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from ssl import CERT_NONE

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

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
'''


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