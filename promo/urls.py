from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'promo', PromoViewSet, basename='promo')
# router.register(r'promo-entries', PromoCountViewSet,)
promo_count_viewset = PromoCountViewSet.as_view({
    'get': 'calculate_codes',
})

urlpatterns = [
    path('', include(router.urls)),
    path('promo-entries/monthly/', PromoMonthlyView.as_view(),),
    path('promo-entries/calculate/', PromoCountViewSet.as_view, name='promo-count-calculate'),
    path('fetch-promo/', FetchPromoView.as_view(),),
]
