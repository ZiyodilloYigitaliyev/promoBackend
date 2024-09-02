from django.db import models
from django.utils import timezone


class PostbackRequest(models.Model):
    msisdn = models.CharField(max_length=15)  # Abonentning telefon raqami
    opi = models.IntegerField()  # Operator ID (22, 23 yoki 27)
    short_number = models.CharField(max_length=10)  # Qisqa raqam (masalan, 7500)
    text = models.TextField()  # Abonentdan kelgan xabar
    # received_at = models.DateTimeField(default=timezone.now)  # So'rov kelgan vaqt

    def __str__(self):
        return f"{self.msisdn} - {self.short_number} - {self.text[:50]}"

class SMSResponse(models.Model):
    postback_request = models.OneToOneField(PostbackRequest, on_delete=models.CASCADE, related_name='response')
    response_text = models.TextField()  # Yuborilgan javob xabari
    sent_at = models.DateTimeField(default=timezone.now)  # Javob yuborilgan vaqt
    status_code = models.IntegerField()  # API dan qaytgan status kodi (masalan, 200, 500)

    def __str__(self):
        return f"Response to {self.postback_request.msisdn} - Status: {self.status_code}"




# class Promo(models.Model):
#     tel = models.CharField(max_length=15)
#     sent_count = models.IntegerField(default=0)
#
#     def __str__(self):
#         return self.tel

# class PromoEntry(models.Model):
#     msisdn = models.CharField(max_length=50)
#     opi = models.CharField(max_length=2)
#     short_number = models.CharField(max_length=10)
#     message = models.TextField()
#
#     def __str__(self):
#         return f"{self.msisdn} - {self.short_number}"



# class SMSLog(models.Model):
#     msisdn = models.CharField(max_length=50)
#     opi = models.CharField(max_length=2)
#     short_number = models.CharField(max_length=10)
#     message = models.TextField()
#
#     def __str__(self):
#         return f"{self.msisdn} - {self.short_number}"


# class PromoCode(models.Model):
#     code = models.CharField(max_length=50)