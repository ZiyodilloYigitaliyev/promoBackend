# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import PostbackRequest, Notification
import requests

from django.utils import timezone
from celery import shared_task
import requests


@shared_task
def send_notification_on_new_promo_opi_27():
    # Bugungi sanani olamiz
    today = timezone.now().date()

    # Bugungi sanadan boshlab Notification modelidagi xabarlarni olamiz
    notifications = Notification.objects.filter(date=today)

    # Faqat opi=27 bo'lgan va bugun qo'shilgan promo kodlar uchun
    new_promos_for_opi_27 = PostbackRequest.objects.filter(opi=23, created_at__date=today)

    if new_promos_for_opi_27.exists():
        # Har bir notification uchun xabar yuborish
        for notification in notifications:
            for promo_request in new_promos_for_opi_27:
                sms_api_url = "https://cp.vaspool.com/api/v1/sms/send?token=sUt1TCRZdhKTWXFLdOuy39JByFlx2"
                params = {
                    'opi': promo_request.opi,
                    'msisdn': promo_request.msisdn,
                    'short_number': promo_request.short_number,
                    'message': notification.text
                }
                requests.get(sms_api_url, params=params)

