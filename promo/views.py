import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .api import fetch_and_save_promo
from .models import Promo, PromoEntry
from .serializers import PromoSerializer, PromoEntrySerializer
from django.utils import timezone

class PromoViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        GET so'rovi: Barcha promo ma'lumotlarini ro'yxat qilib qaytaradi.
        """
        promos = Promo.objects.all()
        serializer = PromoSerializer(promos, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        POST so'rovi: Promo ma'lumotlarini yaratish va saqlash.
        """
        tel = request.data.get('tel')
        promo_code = request.data.get('promo')

        promo_obj, created = Promo.objects.get_or_create(tel=tel)
        PromoEntry.objects.create(promo=promo_obj, code=promo_code)
        promo_obj.sent_count += 1
        promo_obj.save()

        serializer = PromoSerializer(promo_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        GET so'rovi: Bitta promo ma'lumotini qaytaradi.
        """
        try:
            promo = Promo.objects.get(pk=pk)
        except Promo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PromoSerializer(promo)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        PUT so'rovi: Promo ma'lumotlarini yangilash.
        """
        try:
            promo = Promo.objects.get(pk=pk)
        except Promo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        promo.tel = request.data.get('tel', promo.tel)
        promo.sent_count = request.data.get('sent_count', promo.sent_count)
        promo.save()

        serializer = PromoSerializer(promo)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        DELETE so'rovi: Promo ma'lumotlarini o'chirish.
        """
        try:
            promo = Promo.objects.get(pk=pk)
        except Promo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        promo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# **************************************************
class FetchPromoView(APIView):
    def get(self, request):
        promo_entry = fetch_and_save_promo()
        if promo_entry:
            serializer = PromoEntrySerializer(promo_entry)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Failed to fetch promo."}, status=status.HTTP_400_BAD_REQUEST)

# ************ xisoblash ***********************
class PromoCountViewSet(viewsets.ViewSet):

    def calculate_codes(self, request):
        """
        GET so'rovi: Barcha promo kodlar sonini hisoblab, 3149 ga ko'paytiradi.
        """
        entries = PromoEntry.objects.all()
        code_count = entries.count()
        multiplied_value = code_count * 3149

        result = {
            'code_count': code_count,
            'multiplied_value': multiplied_value
        }

        return Response(result, status=status.HTTP_200_OK)