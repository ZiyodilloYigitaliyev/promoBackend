from django.urls import path
from .views import *





urlpatterns = [
    path('postback-callback/', PromoAPIView.as_view()),

    # path('promo-entries/monthly/', PromoMonthlyView.as_view()),

    # path('promo-entries/calculate/', PromoCountViewSet.as_view()),
    # path('postback-callback/', PostbackCallbackViews.as_view(), name='postback-callback'),

]
