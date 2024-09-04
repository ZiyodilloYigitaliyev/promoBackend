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
            try:
                promo = Promo.objects.get(promo_text=text)
            except Promo.DoesNotExist:
                custom_message = "Jo’natilgan Promokod noto’g’ri!"
                return self.send_sms(msisdn, opi, short_number, custom_message)

            # PromoEntry modelida ushbu promokod oldin ro'yxatdan o'tganligini tekshirish
            if PromoEntry.objects.filter(text=text, PostbackRequest__msisdn=msisdn).exists():
                custom_message = "Quyidagi Promokod avval ro’yxatdan o’tgazilgan!"
                return self.send_sms(msisdn, opi, short_number, custom_message)

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
        """
        GET so'rovi: Oylik promo ma'lumotlarini qaytaradi.
        """
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if month and year:
            try:
                month = int(month)
                year = int(year)

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
                ).select_related('postback_request')

                # Foydalanuvchilar
                users_in_month = PostbackRequest.objects.filter(
                    promoentry__created_at__range=(start_date, end_date)
                ).distinct()

                # Promolarni guruhlash
                promos_grouped = {}
                for entry in promos_in_month:
                    postback_request = entry.postback_request
                    if postback_request not in promos_grouped:
                        promos_grouped[postback_request] = []
                    promos_grouped[postback_request].append({
                        "id": entry.id,
                        "text": entry.text,
                        "created_at": entry.created_at.isoformat()
                    })

                result = {
                    "month": calendar.month_name[month].lower(),
                    "promos": {
                        postback_request.msisdn: {
                            "sent_count": len(promos),
                            "promos": promos
                        }
                        for postback_request, promos in promos_grouped.items()
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
                    timezone.datetime(month.year, month.month, calendar.monthrange(month.year, month.month)[1], 23, 59, 59))

                # Promo kodlar
                promos_in_month = PromoEntry.objects.filter(
                    created_at__range=(start_date, end_date)
                ).select_related('postback_request')

                # Foydalanuvchilar
                users_in_month = PostbackRequest.objects.filter(
                    promoentry__created_at__range=(start_date, end_date)
                ).distinct()

                # Promolarni guruhlash
                promos_grouped = {}
                for entry in promos_in_month:
                    postback_request = entry.postback_request
                    if postback_request not in promos_grouped:
                        promos_grouped[postback_request] = []
                    promos_grouped[postback_request].append({
                        "id": entry.id,
                        "text": entry.text,
                        "created_at": entry.created_at.isoformat()
                    })

                result[month_name] = {
                    "promos": {
                        postback_request.msisdn: {
                            "sent_count": len(promos),
                            "promos": promos
                        }
                        for postback_request, promos in promos_grouped.items()
                    },
                    "users": users_in_month.count()
                }

        return Response(result, status=status.HTTP_200_OK)

class PromoEntryList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        entries = PromoEntry.objects.all()
        serializer = PromoEntrySerializer(entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PromoCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = PromoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
