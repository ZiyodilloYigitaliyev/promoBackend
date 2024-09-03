import requests

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.functions import TruncMonth
from django.db.models import Count
import calendar
from datetime import timedelta, datetime
from rest_framework.viewsets import ViewSet

from .serializers import *
from django.utils import timezone


class PostbackCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        msisdn = request.query_params.get('msisdn')
        opi = request.query_params.get('opi')
        short_number = request.query_params.get('short_number')
        text = request.query_params.get('message')

        if msisdn and opi and short_number and text:
            # Ma'lumotlarni bazaga saqlash
            data = {
                'msisdn': msisdn,
                'opi': opi,
                'short_number': short_number,
                'text': text
            }
            serializer = PostbackRequestSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                custom_message = (
                    "Promo kodingizni qabul qilindi!\n"
                    "“Boriga baraka” shousida ishtirok etganingiz uchun tashakkur"
                )
                # GET so'rovini API ga yuborish
                sms_api_url = "https://cp.vaspool.com/api/v1/sms/send?token=sUt1TCRZdhKTWXFLdOuy39JByFlx2"
                params = {
                    'opi': opi,
                    'msisdn': msisdn,
                    'short_number': short_number,
                    'message': custom_message
                }

                try:
                    sms_response = requests.get(sms_api_url, params=params)
                    sms_response.raise_for_status()
                    # Agar muvaffaqiyatli bo'lsa
                    return Response({'message': 'Data saved and SMS sent successfully'}, status=status.HTTP_201_CREATED)
                except requests.RequestException as e:
                    return Response({"error": "Failed to send SMS", "details": str(e)},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

#     ********************* Monthly date *************************
# class PromoMonthlyView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         # URL parametrlarini olish
#         month = request.query_params.get('month')
#         year = request.query_params.get('year')
#
#         # Agar month va year parametrlar kiritilgan bo'lsa
#         if month and year:
#             try:
#                 month = int(month)
#                 year = int(year)
#                 # Oyni va yilni tekshirish
#                 if month < 1 or month > 12:
#                     raise ValueError("Month must be between 1 and 12.")
#                 if year < 1900:
#                     raise ValueError("Year must be greater than 1900.")
#
#                 start_date = timezone.make_aware(timezone.datetime(year, month, 1))
#                 end_date = timezone.make_aware(
#                     timezone.datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59))
#
#                 # Promo kodlar
#                 promos_in_month = PromoEntry.objects.filter(
#                     created_at__range=(start_date, end_date)
#                 ).select_related('promo')
#
#                 # Foydalanuvchilar
#                 users_in_month = Promo.objects.filter(
#                     promos__created_at__range=(start_date, end_date)
#                 ).distinct()
#
#                 # Promolarni guruhlash
#                 promos_grouped = {}
#                 for entry in promos_in_month:
#                     promo = entry.promo
#                     if promo not in promos_grouped:
#                         promos_grouped[promo] = []
#                     promos_grouped[promo].append({
#                         "id": entry.id,
#                         "code": entry.code,
#                         "created_at": entry.created_at.isoformat()
#                     })
#
#                 result = {
#                     "month": calendar.month_name[month].lower(),
#                     "promos": {
#                         promo.tel: {
#                             "sent_count": len(promos),
#                             "promos": promos
#                         }
#                         for promo, promos in promos_grouped.items()
#                     },
#                     "users": users_in_month.count()
#                 }
#             except ValueError as e:
#                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             # Agar month va year parametrlar kiritilmagan bo'lsa, barcha oylardagi ma'lumotlarni qaytaradi
#             entries = PromoEntry.objects.annotate(month=TruncMonth('created_at')).values('month').distinct()
#
#             result = {}
#             for entry in entries:
#                 month = entry['month']
#                 month_name = month.strftime("%B").lower()
#                 start_date = timezone.make_aware(timezone.datetime(month.year, month.month, 1))
#                 end_date = timezone.make_aware(
#                     timezone.datetime(month.year, month.month, calendar.monthrange(month.year, month.month)[1], 23, 59,
#                                       59))
#
#                 # Promo kodlar
#                 promos_in_month = PromoEntry.objects.filter(
#                     created_at__range=(start_date, end_date)
#                 ).select_related('promo')
#
#                 # Foydalanuvchilar
#                 users_in_month = Promo.objects.filter(
#                     promos__created_at__range=(start_date, end_date)
#                 ).distinct()
#
#                 # Promolarni guruhlash
#                 promos_grouped = {}
#                 for entry in promos_in_month:
#                     promo = entry.promo
#                     if promo not in promos_grouped:
#                         promos_grouped[promo] = []
#                     promos_grouped[promo].append({
#                         "id": entry.id,
#                         "code": entry.code,
#                         "created_at": entry.created_at.isoformat()
#                     })
#
#                 result[month_name] = {
#                     "promos": {
#                         promo.tel: {
#                             "sent_count": len(promos),
#                             "promos": promos
#                         }
#                         for promo, promos in promos_grouped.items()
#                     },
#                     "users": users_in_month.count()
#                 }
#
#         return Response(result, status=status.HTTP_200_OK)



