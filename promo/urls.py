from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'promo', PromoViewSet, basename='promo')
# router.register(r'promo-entries', PromoCountViewSet,)

urlpatterns = [
    path('', include(router.urls)),
    path('promo-entries/monthly/', MonthlyPromoView.as_view(),),
    path('promo-entries/calculate/', PromoCountViewSet.as_view({'get': 'calculate_codes'}),),
    path('fetch-promo/', FetchPromoView.as_view(),),
]
