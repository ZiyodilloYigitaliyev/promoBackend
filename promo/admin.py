from django.contrib import admin
from .models import *

@admin.register(PostbackRequest)
class PostbackRequestAdmin(admin.ModelAdmin):
    list_display = ('msisdn', 'opi', 'short_number', 'sent_count')

class PromoEntryAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_at')
admin.site.register(PromoEntry, PromoEntryAdmin)

class PromoAdmin(admin.ModelAdmin):
    list_display = ['promo_text']  # Admin panelda promo matnini ko'rsatish
    actions = ['delete_selected_promos']

    def delete_selected_promos(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} ta promo muvaffaqiyatli o'chirildi.")
    delete_selected_promos.short_description = 'Tanlangan promolarni o\'chirish'

admin.site.register(Promo, PromoAdmin)


