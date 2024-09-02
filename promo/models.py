from django.db import models
from django.utils import timezone

class Promo(models.Model):
    tel = models.CharField(max_length=15)
    sent_count = models.IntegerField(default=0)

    def __str__(self):
        return self.tel

class PromoEntry(models.Model):
    msisdn = models.CharField(max_length=50)
    opi = models.CharField(max_length=2)
    short_number = models.CharField(max_length=10)
    message = models.TextField()

    def __str__(self):
        return f"{self.msisdn} - {self.short_number}"

    def __str__(self):
        return self.code

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