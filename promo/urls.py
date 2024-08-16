from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *




urlpatterns = [
    path('promo/', PromoAPIView.as_view()),
    path('promo-entries/monthly/', PromoMonthlyView.as_view()),
    path('promo-entries/calculate/', PromoCountViewSet.as_view()),
    path('fetch-promo/', FetchPromoView.as_view()),
    path('week-phone-numbers/', RecentPhoneNumbersView.as_view()),
]
