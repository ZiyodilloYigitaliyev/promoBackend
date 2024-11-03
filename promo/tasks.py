# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import PostbackRequest, Notification
import requests

@shared_task
def send_daily_notifications():
    today = timezone.now().date()
    notifications = Notification.objects.filter(date=today)

    for notification in notifications:
        requests_for_opi_23 = PostbackRequest.objects.filter(opi=23)

        for request in requests_for_opi_23:
            sms_api_url = "https://cp.vaspool.com/api/v1/sms/send?token=sUt1TCRZdhKTWXFLdOuy39JByFlx2"
            params = {
                'opi': request.opi,
                'msisdn': request.msisdn,
                'short_number': request.short_number,
                'message': notification.text
            }
            requests.get(sms_api_url, params=params)
