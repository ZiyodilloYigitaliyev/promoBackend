from django.contrib import admin
from .models import *

@admin.register(PostbackRequest)
class PostbackRequestAdmin(admin.ModelAdmin):
    list_display = ('msisdn', 'opi', 'short_number', 'sent_count')

class PromoEntryAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_at')
admin.site.register(PromoEntry, PromoEntryAdmin)

class PromoAdmin(admin.ModelAdmin):
    list_display = ('id', 'promo_text')

admin.site.register(Promo, PromoAdmin)


