from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Django konfiguratsiyasini yuklash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

app = Celery('promo')

# Konfiguratsiyalarni olish
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
