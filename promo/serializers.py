from rest_framework import serializers
from .models import *


class PromoEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoEntry
        fields = '__all__'

class PostbackRequestSerializer(serializers.ModelSerializer):
    # entries = PromoEntrySerializer(many=True, read_only=True)
    messages = PromoEntrySerializer(source='promoentry_set', many=True, read_only=True)
    class Meta:
        model = PostbackRequest
        fields = '__all__'


class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = '__all__'

