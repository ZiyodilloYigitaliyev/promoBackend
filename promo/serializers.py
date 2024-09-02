from rest_framework import serializers
from .models import *

class PromoEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoEntry
        fields = ['id', 'code', 'created_at']

class PromoSerializer(serializers.ModelSerializer):
    promos = PromoEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Promo
        fields = ['id', 'tel', 'sent_count', 'promos']

class SMSLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSLog
        fields = ['msisdn', 'opi', 'short_number', 'text', 'received_at']