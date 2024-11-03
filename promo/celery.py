import os
from celery import Celery

app = Celery('promo')

# Broker va natija backend URL'ni Redis uchun o'rnating
app.conf.broker_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
app.conf.result_backend = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')