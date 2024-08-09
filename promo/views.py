import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Count
from datetime import timedelta

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
            return Response({"detail": "Promo code already exists or failed to fetch promo."}, status=status.HTTP_400_BAD_REQUEST)

# ************ xisoblash ***********************
class PromoCountViewSet(viewsets.ViewSet):

    def calculate_codes(self, request):
        """
        GET so'rovi: Promo kodlar va telefon raqamlarni hisoblab, ma'lum vaqt oralig'iga ko'ra filterlaydi.
        """
        filter_by = request.query_params.get('filter_by', 'day')

        if filter_by == 'month':
            start_date = timezone.now() - timedelta(days=30)
        elif filter_by == 'week':
            start_date = timezone.now() - timedelta(weeks=1)
        else:  # 'day' yoki default holat
            start_date = timezone.now() - timedelta(days=1)

        # Tanlangan vaqt oralig'iga ko'ra filterlash
        filtered_entries = PromoEntry.objects.filter(created_at__gte=start_date)
        code_count = filtered_entries.count()
        multiplied_value = code_count * 3149

        # Promo modeli orqali barcha noyob telefon raqamlarini hisoblash
        total_tel_count = Promo.objects.filter(promos__created_at__gte=start_date).distinct().count()

        result = {
            'code_count': code_count,
            'sum': multiplied_value,
            'users': total_tel_count
        }

        return Response(result, status=status.HTTP_200_OK)