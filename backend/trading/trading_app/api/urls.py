


from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TradingStrategyViewSet, TradeViewSet, TradingDashboardViewSet, PositionViewSet, ExchangeKeyViewSet

router = DefaultRouter()
router.register(r'strategies', TradingStrategyViewSet)
router.register(r'trades', TradeViewSet)
router.register(r'positions', PositionViewSet)
router.register(r'exchange-keys', ExchangeKeyViewSet, basename='exchange-keys')
# router.register(r'dashboard', TradingDashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
    # path('ws/', include('trading.websockets.urls')),
]