from django.contrib import admin
from .models import *

@admin.register(PostbackRequest)
class PostbackRequestAdmin(admin.ModelAdmin):
    list_display = ('msisdn', 'opi', 'short_number', 'text')





