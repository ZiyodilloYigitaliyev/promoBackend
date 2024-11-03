# promo/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Django konfiguratsiyalarini yuklash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promo.settings')

app = Celery('promo')

# Django konfiguratsiyalarini Celery ga yuklash
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tasklarni avtomatik aniqlash
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
