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

                # GET so'rovini API ga yuborish
                sms_api_url = "https://cp.vaspool.com/api/v1/sms/send"
                params = {
                    'token': 'sUt1TCRZdhKTWXFLdOuy39JByFlx2',
                    'msisdn': msisdn,
                    'short_number': short_number,
                    'message': text  # Yuboriladigan xabar
                }

                try:
                    sms_response = requests.get(sms_api_url, params=params)
                    sms_response.raise_for_status()

                    # Agar SMS yuborish muvaffaqiyatli bo'lsa
                    return Response({'message': 'Data saved and SMS sent successfully'}, status=status.HTTP_201_CREATED)
                except requests.RequestException as e:
                    # Agar SMS yuborishda xatolik yuz bersa
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



# ************ xisoblash ***********************
# class PromoCountViewSet(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         """
#         GET so'rovi: Promo kodlar va telefon raqamlarni hisoblab, ma'lum vaqt oralig'iga ko'ra filterlaydi.
#         """
#         # Parametrlarni olish
#         month = request.query_params.get('month')
#         year = request.query_params.get('year')
#
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
#                 # O'sha oy va yil uchun boshlanish va tugash vaqtlarini aniqlash
#                 start_date = timezone.make_aware(timezone.datetime(year, month, 1))
#                 end_date = timezone.make_aware(
#                     timezone.datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59))
#
#                 # Filtrlangan promo kodlar
#                 filtered_entries = PromoEntry.objects.filter(created_at__range=(start_date, end_date))
#                 code_count = filtered_entries.count()
#             except ValueError as e:
#                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             # Agar month va year parametrlar ko'rsatilmagan bo'lsa, barcha vaqt bo'yicha ma'lumotlar
#             filtered_entries = PromoEntry.objects.all()
#             code_count = filtered_entries.count()
#             start_date = None  # Barcha vaqt
#             end_date = None
#
#         multiplied_value = code_count * 3149
#
#         # Barcha noyob telefon raqamlarini hisoblash
#         if start_date and end_date:
#             total_tel_count = Promo.objects.filter(promos__created_at__range=(start_date, end_date)).distinct().count()
#         else:
#             total_tel_count = Promo.objects.distinct().count()
#
#         result = {
#             'code_count': code_count,
#             'sum': multiplied_value,
#             'users': total_tel_count
#         }
#
#         return Response(result, status=status.HTTP_200_OK)


#
# class PostbackCallbackViews(APIView):
#         permission_classes = [AllowAny]
#
#         def post(self, request, *args, **kwargs):
#             # So'rovdan kerakli parametrlarni olish
#             msisdn = request.data.get('msisdn')
#             opi = request.data.get('opi')
#             short_number = request.data.get('short_number')
#             text = request.data.get('text')
#
#             # SMSLog ga yozuv qo'shish
#             sms_log = SMSLog.objects.create(
#                 msisdn=msisdn,
#                 opi=opi,
#                 short_number=short_number,
#                 message=text
#             )
#
#             # SMS yuborish uchun API'ga so'rov qilish
#             sms_api_url = "https://cp.vaspool.com/api/v1/sms/send"
#             sms_api_token = "sUt1TCRZdhKTWXFLdOuy39JByFlx2"  # Tokenni o'zingizda saqlang yoki settings'dan oling
#             sms_data = {
#                 'msisdn': msisdn,
#                 'opi': opi,
#                 'short_number': short_number,
#                 'message': text,
#                 'token': sms_api_token
#             }
#
#             response = requests.post(sms_api_url, data=sms_data)
#
#             if response.status_code == 200:
#                 # API muvaffaqiyatli javob berdi
#                 response_message = "Sizning so'rovingiz qabul qilindi"
#                 return Response({'status': 'success', 'message': response_message}, status=status.HTTP_200_OK)
#             else:
#                 # API muvaffaqiyatsiz javob berdi
#                 return Response({'status': 'error', 'message': 'SMS yuborishda xatolik yuz berdi'},
#                                 status=status.HTTP_400_BAD_REQUEST)

