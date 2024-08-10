from django.db import models
from django.utils import timezone

class Promo(models.Model):
    tel = models.CharField(max_length=15)
    sent_count = models.IntegerField(default=0)

    def __str__(self):
        return self.tel

class PromoEntry(models.Model):
    promo = models.ForeignKey(Promo, related_name='promos', on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.code
