from rest_framework import serializers
from .models import *



class PostbackRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostbackRequest
        fields = '__all__'

