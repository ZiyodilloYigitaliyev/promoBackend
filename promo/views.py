import requests
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models.functions import TruncMonth
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

        custom_message = ""

        if msisdn and opi and short_number and text:
            # Promo modelida promokod mavjudligini tekshirish
            promo = Promo.objects.filter(promo_text=text).first()
            if promo is None:
                custom_message = "Jo’natilgan Promokod noto’g’ri!"
                return self.send_sms(msisdn, opi, short_number, custom_message)

            # PromoEntry modelida ushbu promokod oldin ro'yxatdan o'tganligini tekshirish
            if PromoEntry.objects.filter(text=text, PostbackRequest__msisdn=msisdn).exists():
                custom_message = "Quyidagi Promokod avval ro’yxatdan o’tkazilgan!"
                return self.send_sms(msisdn, opi, short_number, custom_message)

            # Agar msisdn bazada mavjud bo'lsa, faqat sent_count ni oshirish va yangi promo saqlash
            postback_request = PostbackRequest.objects.filter(msisdn=msisdn).first()
            if postback_request:
                # Mavjud PostbackRequest uchun sent_count ni oshirish
                postback_request.sent_count += 1
                postback_request.save()

                # Yangi PromoEntry ni mavjud PostbackRequestga bog'lash
                PromoEntry.objects.create(
                    PostbackRequest=postback_request,
                    text=text,
                    created_at=timezone.now()
                )
            else:
                # Yangi PostbackRequest va PromoEntry yaratish
                postback_request = PostbackRequest.objects.create(
                    msisdn=msisdn,
                    opi=opi,
                    short_number=short_number,
                    sent_count=1
                )

                PromoEntry.objects.create(
                    PostbackRequest=postback_request,
                    text=text,
                    created_at=timezone.now()
                )

            custom_message = (
                "Tabriklaymiz! Promokod qabul qilindi!\n"
                "\"Boriga baraka\" ko'rsatuvini har Juma soat 21:00 da Jonli efirda tomosha qiling!"
            )
            return self.send_sms(msisdn, opi, short_number, custom_message)
        else:
            return Response({"error": "Failed to send SMS"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_sms(self, msisdn, opi, short_number, custom_message):
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
            return Response({'message': custom_message}, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response({"error": "Failed to send SMS", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     ********************* Monthly date *************************
class PromoMonthlyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        # Agar month va year parametrlar kiritilgan bo'lsa, o'sha oyni filtrlaymiz
        if month and year:
            try:
                month = int(month)
                year = int(year)

                if month < 1 or month > 12:
                    raise ValueError("Month must be between 1 and 12.")
                if year < 1900:
                    raise ValueError("Year must be greater than 1900.")

                # Oylik sana oralig'ini yaratish
                start_date = timezone.make_aware(timezone.datetime(year, month, 1))
                end_date = timezone.make_aware(
                    timezone.datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59))

                # Berilgan oy uchun PromoEntry yozuvlarini olish
                promos_in_month = PromoEntry.objects.filter(
                    created_at__range=(start_date, end_date)
                ).select_related('PostbackRequest')

                # PostbackRequest'ni promos bilan bog'lash
                promos_grouped = {}
                for entry in promos_in_month:
                    postback_request = entry.PostbackRequest
                    if postback_request.msisdn not in promos_grouped:
                        promos_grouped[postback_request.msisdn] = {
                            "sent_count": 0,
                            "promos": []
                        }

                    # sent_countni har bir foydalanuvchi uchun orttirish
                    promos_grouped[postback_request.msisdn]["sent_count"] += 1
                    # Har bir promo kodni promos ro'yxatiga qo'shish
                    promos_grouped[postback_request.msisdn]["promos"].append({
                        "id": entry.id,
                        "text": entry.text,
                        "created_at": entry.created_at.isoformat()
                    })

                # Foydalanuvchilarni hisoblash
                users_in_month = PostbackRequest.objects.filter(
                    promoentry__created_at__range=(start_date, end_date)
                ).distinct()

                # Natija tuzish
                result = {
                    "month": calendar.month_name[month].lower(),
                    "promos": promos_grouped,
                }

            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Agar month va year kiritilmagan bo'lsa, barcha oylardagi ma'lumotlarni qaytarish
        else:
            entries = PromoEntry.objects.annotate(month=TruncMonth('created_at')).values('month').distinct()

            result = {}
            for entry in entries:
                month = entry['month']
                month_name = month.strftime("%B").lower()
                start_date = timezone.make_aware(timezone.datetime(month.year, month.month, 1))
                end_date = timezone.make_aware(
                    timezone.datetime(month.year, month.month, calendar.monthrange(month.year, month.month)[1], 23, 59,
                                      59))

                # Promolarni olish
                promos_in_month = PromoEntry.objects.filter(
                    created_at__range=(start_date, end_date)
                ).select_related('PostbackRequest')

                # Promolarni guruhlash
                promos_grouped = {}
                for entry in promos_in_month:
                    postback_request = entry.PostbackRequest
                    if postback_request.msisdn not in promos_grouped:
                        promos_grouped[postback_request.msisdn] = {
                            "sent_count": 0,
                            "promos": []
                        }

                    promos_grouped[postback_request.msisdn]["sent_count"] += 1
                    promos_grouped[postback_request.msisdn]["promos"].append({
                        "id": entry.id,
                        "text": entry.text,
                        "created_at": entry.created_at.isoformat()
                    })

                # Foydalanuvchilarni olish
                users_in_month = PostbackRequest.objects.filter(
                    promoentry__created_at__range=(start_date, end_date)
                ).distinct()

                result[month_name] = {
                    "promos": promos_grouped,
                    "users": users_in_month.count()
                }

        return Response(result, status=status.HTTP_200_OK)

class PromoEntryList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            # Barcha PostbackRequest yozuvlarini olish
            postback_requests = PostbackRequest.objects.all()
            # Serializer orqali ma'lumotlarni qayta ishlash
            serializer = PostbackRequestSerializerSent(postback_requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PromoCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Faylni request dan olish
        promo_file = request.FILES.get('promo_file', None)

        if not promo_file:
            return Response({"error": "Promo kodlarni o'z ichiga olgan faylni yuklang."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Faylni o'qish va string qilib dekodlash
        try:
            content = promo_file.read().decode('utf-8')
            promo_codes = content.splitlines()
        except Exception as e:
            return Response({"error": "Faylni o'qishda xatolik yuz berdi."}, status=status.HTTP_400_BAD_REQUEST)

        # Har bir promo kodni bazaga saqlash
        for code in promo_codes:
            code = code.strip()  # Bo'sh joylarni olib tashlaymiz
            if code:  # Agar promo kod bo'sh bo'lmasa
                # Promo kodni bazaga qo'shish
                Promo.objects.get_or_create(promo_text=code)

        return Response({"message": "Promo kodlar muvaffaqiyatli saqlandi."}, status=status.HTTP_201_CREATED)

# class PromoCreateView(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         serializer = PromoSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
