from celery import shared_task
from django.utils import timezone
from .models import PostbackRequest, Notification
import requests


@shared_task
def send_daily_notifications():
    today = timezone.now().date()
    notification = Notification.objects.filter(date=today).first()

    if not notification:
        return "No notifications for today"

    recipients = PostbackRequest.objects.filter(opi=23)
    sms_api_url = "https://cp.vaspool.com/api/v1/sms/send?token=sUt1TCRZdhKTWXFLdOuy39JByFlx2"
    custom_message = notification.text
    errors = []

    for recipient in recipients:
        params = {
            'opi': recipient.opi,
            'msisdn': recipient.msisdn,
            'short_number': recipient.short_number,
            'message': custom_message
        }

        try:
            response = requests.get(sms_api_url, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            errors.append({'msisdn': recipient.msisdn, 'error': str(e)})

    if errors:
        return {"status": "Some notifications failed", "errors": errors}

    return "All notifications sent successfully"
