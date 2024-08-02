from django.contrib import admin
from .models import Promo, PromoEntry

class PromoEntryInline(admin.TabularInline):
    model = PromoEntry
    extra = 1

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('tel', 'sent_count', 'get_promos', 'get_multiplied_value')
    search_fields = ('tel',)
    inlines = [PromoEntryInline]

    def get_promos(self, obj):
        """
        Promo modelidagi har bir `Promo` obyekti uchun tegishli `PromoEntry` kodlarini ko'rsatadi.
        """
        return ", ".join([entry.code for entry in obj.promos.all()])
    get_promos.short_description = 'Promo Codes'

    # def get_code_count(self, obj):
    #     """
    #     Har bir `Promo` obyekti uchun uning tegishli `PromoEntry` obyektlarining sonini hisoblaydi.
    #     """
    #     return obj.promos.count()
    # get_code_count.short_description = 'Code Count'

    def get_multiplied_value(self, obj):
        """
        Har bir `Promo` obyekti uchun uning tegishli `PromoEntry` obyektlarining sonini 3149 ga ko'paytiradi.
        """
        return obj.promos.count() * 3149
    get_multiplied_value.short_description = 'Multiplied Value'

@admin.register(PromoEntry)
class PromoEntryAdmin(admin.ModelAdmin):
    list_display = ('promo', 'code', 'created_at')
    search_fields = ('code', 'promo__tel')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
