from django.contrib import admin
from .models import *

@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['msisdn', 'opi', 'short_number', 'message']

class PromoEntryInline(admin.TabularInline):
    model = PromoEntry
    extra = 1

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('tel', 'sent_count', 'get_promos', 'get_multiplied_value')
    search_fields = ('tel',)
    inlines = [PromoEntryInline]

    def get_promos(self, obj):
        return ", ".join([entry.code for entry in obj.promos.all()])
    get_promos.short_description = 'Promo Codes'

    # def get_code_count(self, obj):
    #
    #     return obj.promos.count()
    # get_code_count.short_description = 'Code Count'

    def get_multiplied_value(self, obj):
        return obj.promos.count() * 3149
    get_multiplied_value.short_description = 'Multiplied Value'

@admin.register(PromoEntry)
class PromoEntryAdmin(admin.ModelAdmin):
    list_display = ('promo', 'code', 'created_at')
    search_fields = ('code', 'promo__tel')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
