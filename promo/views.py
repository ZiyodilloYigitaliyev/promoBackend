import requests

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.functions import TruncMonth
from django.db.models import Count
import calendar
from datetime import timedelta, datetime

from rest_framework.viewsets import ViewSet

from .api import fetch_and_save_promo
from .models import Promo, PromoEntry
from .serializers import PromoSerializer, PromoEntrySerializer
from django.utils import timezone


class PromoAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):
        """
        GET so'rovi: Barcha promo ma'lumotlarini yoki bitta promo ma'lumotini qaytaradi.
        """
        if pk:
            try:
                promo = Promo.objects.get(pk=pk)
            except Promo.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            serializer = PromoSerializer(promo)
            return Response(serializer.data)
        else:
            promos = Promo.objects.all()
            serializer = PromoSerializer(promos, many=True)
            return Response(serializer.data)

    def post(self, request):
        """
        POST so'rovi: Yangi promo ma'lumotlarini yaratadi.
        """
        tel = request.data.get('tel')
        promo_code = request.data.get('promo')

        # Promo obj yaratish yoki olish
        promo_obj, created = Promo.objects.get_or_create(tel=tel)

        # Promo kod oldin yuborilganligini tekshirish
        if PromoEntry.objects.filter(promo=promo_obj, code=promo_code).exists():
            return Response(
                {"detail": "Bu promokod allaqachon yuborilgan."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Promokodni PromoEntry ga saqlash va sent_count ni oshirish
        PromoEntry.objects.create(promo=promo_obj, code=promo_code)
        promo_obj.sent_count += 1
        promo_obj.save()

        serializer = PromoSerializer(promo_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




#     ********************* Monthly date *************************
class PromoMonthlyView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # URL parametrlarini olish
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        # Agar month va year parametrlar kiritilgan bo'lsa
        if month and year:
            try:
                month = int(month)
                year = int(year)
                # Oyni va yilni tekshirish
                if month < 1 or month > 12:
                    raise ValueError("Month must be between 1 and 12.")
                if year < 1900:
                    raise ValueError("Year must be greater than 1900.")

                start_date = timezone.make_aware(timezone.datetime(year, month, 1))
                end_date = timezone.make_aware(
                    timezone.datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59))

                # Promo kodlar
                promos_in_month = PromoEntry.objects.filter(
                    created_at__range=(start_date, end_date)
                ).select_related('promo')

                # Foydalanuvchilar
                users_in_month = Promo.objects.filter(
                    promos__created_at__range=(start_date, end_date)
                ).distinct()

                # Promolarni guruhlash
                promos_grouped = {}
                for entry in promos_in_month:
                    promo = entry.promo
                    if promo not in promos_grouped:
                        promos_grouped[promo] = []
                    promos_grouped[promo].append({
                        "id": entry.id,
                        "code": entry.code,
                        "created_at": entry.created_at.isoformat()
                    })

                result = {
                    "month": calendar.month_name[month].lower(),
                    "promos": {
                        promo.tel: {
                            "sent_count": len(promos),
                            "promos": promos
                        }
                        for promo, promos in promos_grouped.items()
                    },
                    "users": users_in_month.count()
                }
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Agar month va year parametrlar kiritilmagan bo'lsa, barcha oylardagi ma'lumotlarni qaytaradi
            entries = PromoEntry.objects.annotate(month=TruncMonth('created_at')).values('month').distinct()

            result = {}
            for entry in entries:
                month = entry['month']
                month_name = month.strftime("%B").lower()
                start_date = timezone.make_aware(timezone.datetime(month.year, month.month, 1))
                end_date = timezone.make_aware(
                    timezone.datetime(month.year, month.month, calendar.monthrange(month.year, month.month)[1], 23, 59,
                                      59))

                # Promo kodlar
                promos_in_month = PromoEntry.objects.filter(
                    created_at__range=(start_date, end_date)
                ).select_related('promo')

                # Foydalanuvchilar
                users_in_month = Promo.objects.filter(
                    promos__created_at__range=(start_date, end_date)
                ).distinct()

                # Promolarni guruhlash
                promos_grouped = {}
                for entry in promos_in_month:
                    promo = entry.promo
                    if promo not in promos_grouped:
                        promos_grouped[promo] = []
                    promos_grouped[promo].append({
                        "id": entry.id,
                        "code": entry.code,
                        "created_at": entry.created_at.isoformat()
                    })

                result[month_name] = {
                    "promos": {
                        promo.tel: {
                            "sent_count": len(promos),
                            "promos": promos
                        }
                        for promo, promos in promos_grouped.items()
                    },
                    "users": users_in_month.count()
                }

        return Response(result, status=status.HTTP_200_OK)



# ************ xisoblash ***********************
class PromoCountViewSet(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        GET so'rovi: Promo kodlar va telefon raqamlarni hisoblab, ma'lum vaqt oralig'iga ko'ra filterlaydi.
        """
        # Parametrlarni olish
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if month and year:
            try:
                month = int(month)
                year = int(year)
                # Oyni va yilni tekshirish
                if month < 1 or month > 12:
                    raise ValueError("Month must be between 1 and 12.")
                if year < 1900:
                    raise ValueError("Year must be greater than 1900.")

                # O'sha oy va yil uchun boshlanish va tugash vaqtlarini aniqlash
                start_date = timezone.make_aware(timezone.datetime(year, month, 1))
                end_date = timezone.make_aware(
                    timezone.datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59))

                # Filtrlangan promo kodlar
                filtered_entries = PromoEntry.objects.filter(created_at__range=(start_date, end_date))
                code_count = filtered_entries.count()
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Agar month va year parametrlar ko'rsatilmagan bo'lsa, barcha vaqt bo'yicha ma'lumotlar
            filtered_entries = PromoEntry.objects.all()
            code_count = filtered_entries.count()
            start_date = None  # Barcha vaqt
            end_date = None

        multiplied_value = code_count * 3149

        # Barcha noyob telefon raqamlarini hisoblash
        if start_date and end_date:
            total_tel_count = Promo.objects.filter(promos__created_at__range=(start_date, end_date)).distinct().count()
        else:
            total_tel_count = Promo.objects.distinct().count()

        result = {
            'code_count': code_count,
            'sum': multiplied_value,
            'users': total_tel_count
        }

        return Response(result, status=status.HTTP_200_OK)

# ************************ WEEK PHONE NUMBERS *******************************

class PostbackCallbackViews(APIView):
    def post(self, request):
        """
        POST so'rovi: Yangi promo ma'lumotlarini yaratadi.
        """
        tel = request.data.get('tel')
        promo_code = request.data.get('promo')

        # Promo obj yaratish yoki olish
        promo_obj, created = Promo.objects.get_or_create(tel=tel)

        # Promo kod oldin yuborilganligini tekshirish
        if PromoEntry.objects.filter(promo=promo_obj, code=promo_code).exists():
            return Response(
                {"detail": "This promo code has already been sent."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Promokodni PromoEntry ga saqlash va sent_count ni oshirish
        PromoEntry.objects.create(promo=promo_obj, code=promo_code)
        promo_obj.sent_count += 1
        promo_obj.save()

        serializer = PromoSerializer(promo_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)