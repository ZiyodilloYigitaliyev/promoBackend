from rest_framework import serializers
from .models import Promo, PromoEntry

class PromoEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoEntry
        fields = ['id', 'code', 'created_at']

class PromoSerializer(serializers.ModelSerializer):
    promos = PromoEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Promo
        fields = ['id', 'tel', 'sent_count', 'promos']
