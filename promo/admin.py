from django.contrib import admin
from .models import *

@admin.register(PostbackRequest)
class PostbackRequestAdmin(admin.ModelAdmin):
    list_display = ('msisdn', 'opi', 'short_number', 'text')


@admin.register(PromoEntry)
class PromoEntryAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_at')

class PromoAdmin(admin.ModelAdmin):
    list_display = ('promo_text',)

admin.site.register(Promo, PromoAdmin)


