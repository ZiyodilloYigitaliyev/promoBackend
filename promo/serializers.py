from rest_framework import serializers
from .models import *


class PromoEntrySerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='text')
    class Meta:
        model = PromoEntry
        fields = ['id', 'code', 'created_at']

class PostbackRequestSerializer(serializers.ModelSerializer):
    # entries = PromoEntrySerializer(many=True, read_only=True)
    messages = PromoEntrySerializer(source='promoentry_set', many=True, read_only=True)
    class Meta:
        model = PostbackRequest
        fields = ['id', 'opi', 'msisdn', 'sent_count', 'messages']


class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = '__all__'

