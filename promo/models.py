from django.db import models
from django.utils import timezone
import pytz

class PostbackRequest(models.Model):
    msisdn = models.CharField(max_length=15)  # Abonentning telefon raqami
    opi = models.IntegerField()  # Operator ID (22, 23 yoki 27)
    short_number = models.CharField(max_length=10)  # Qisqa raqam (masalan, 7500)
    text = models.TextField()  # Abonentdan kelgan xabar
    created_at = models.DateTimeField()  # Ma'lumotlar qo'shilgan vaqt

    def save(self, *args, **kwargs):
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')
        self.created_at = timezone.now().astimezone(uzbekistan_tz)  # Vaqtni O'zbekiston vaqtiga moslashtirish
        super(PostbackRequest, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.msisdn} - {self.short_number} - {self.text[:50]}"















# class PromoCode(models.Model):
#     code = models.CharField(max_length=50)