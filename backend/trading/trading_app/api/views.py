
from datetime import timedelta, datetime
from decimal import Decimal

import logging
from django.db.models.functions import TruncDay, TruncHour
from django.db.models import Sum, Avg, Max, Min
from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import TradingStrategy, Trade, Position
from .serializers import TradingStrategySerializer, TradeSerializer, PositionSerializer, ExchangeKeySerializer
from ..models.exchange_key import ExchangeKey
from ..services.binance_service import BinanceService
from ..services.exchange_factory import ExchangeFactory


logger = logging.getLogger(__name__)


class TradingStrategyViewSet(viewsets.ModelViewSet):
    queryset = TradingStrategy.objects.all()
    serializer_class = TradingStrategySerializer

    @action(detail=True, methods=['POST'])
    def toggle_active(self, request, pk=None):
        """Active ou désactive une stratégie"""
        strategy = self.get_object()
        strategy.is_active = not strategy.is_active
        strategy.save()

        return Response({
            'status': 'success',
            'is_active': strategy.is_active
        })

    @action(detail=True, methods=['POST'])
    def update_parameters(self, request, pk=None):
        """Met à jour les paramètres d'une stratégie"""
        strategy = self.get_object()
        parameters = request.data.get('parameters', {})

        try:
            strategy.update_parameters(parameters)
            return Response({
                'status': 'success',
                'parameters': strategy.parameters
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=['GET'], url_path='pnl-history')
    # def pnl_history(self, request):
    #     """Returns P&L history with period filter"""
    #     try:
    #         period = request.query_params.get('period', 'day')  # по умолчанию 24 часа
    #         end_date = timezone.now()
    #
    #         # Определяем начальную дату на основе периода
    #         if period == 'year':
    #             start_date = end_date - timedelta(days=365)
    #         elif period == 'month':
    #             start_date = end_date - timedelta(days=30)
    #         elif period == 'week':
    #             start_date = end_date - timedelta(days=7)
    #         else:  # day - 24 часа
    #             start_date = end_date - timedelta(days=1)
    #
    #         trades = Trade.objects.filter(
    #             exit_time__range=[start_date, end_date]
    #         ).order_by('exit_time')
    #
    #         # Группируем данные в зависимости от периода
    #         if period == 'day':
    #             # Для 24 часов группируем по часам
    #             trades_data = trades.extra({
    #                 'interval': "date_trunc('hour', exit_time)"
    #             })
    #         else:
    #             # Для остальных периодов группируем по дням
    #             trades_data = trades.extra({
    #                 'interval': "date_trunc('day', exit_time)"
    #             })
    #
    #         grouped_data = trades_data.values('interval').annotate(
    #             value=Sum('profit_loss')
    #         ).order_by('interval')
    #
    #         # Форматируем для фронтенда
    #         result = [{
    #             'time': item['interval'].isoformat(),
    #             'value': float(item['value']) if item['value'] else 0
    #         } for item in grouped_data]
    #
    #         return Response(result)
    #
    #     except Exception as e:
    #         return Response(
    #             {'error': str(e)},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )
    #
    # @action(detail=False, methods=['GET'], url_path='balance-history')
    # def balance_history(self, request):
    #     """Returns balance history with period filter"""
    #     try:
    #         period = request.query_params.get('period', 'day')  # по умолчанию 24 часа
    #         end_date = timezone.now()
    #
    #         # Определяем начальную дату на основе периода
    #         if period == 'year':
    #             start_date = end_date - timedelta(days=365)
    #         elif period == 'month':
    #             start_date = end_date - timedelta(days=30)
    #         elif period == 'week':
    #             start_date = end_date - timedelta(days=7)
    #         else:  # day - 24 часа
    #             start_date = end_date - timedelta(days=1)
    #
    #         positions = Position.objects.filter(
    #             created_at__range=[start_date, end_date]
    #         ).order_by('created_at')
    #
    #         # Группируем данные в зависимости от периода
    #         if period == 'day':
    #             # Для 24 часов группируем по часам
    #             positions_data = positions.extra({
    #                 'interval': "date_trunc('hour', created_at)"
    #             })
    #         else:
    #             # Для остальных периодов группируем по дням
    #             positions_data = positions.extra({
    #                 'interval': "date_trunc('day', created_at)"
    #             })
    #
    #         grouped_data = positions_data.values('interval').annotate(
    #             value=Sum('current_value')
    #         ).order_by('interval')
    #
    #         # Форматируем для фронтенда
    #         result = [{
    #             'time': item['interval'].isoformat(),
    #             'value': float(item['value']) if item['value'] else 0
    #         } for item in grouped_data]
    #
    #         return Response(result)
    #
    #     except Exception as e:
    #         return Response(
    #             {'error': str(e)},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

    @action(detail=False, methods=['GET'], url_path='pnl-history')
    def pnl_history(self, request):
        """Returns P&L history with period filter"""
        try:
            period = request.query_params.get('period', 'day')
            end_date = timezone.now()

            # Определяем период и функцию усечения
            if period == 'year':
                start_date = end_date - timedelta(days=365)
                trunc_func = TruncDay
            elif period == 'month':
                start_date = end_date - timedelta(days=30)
                trunc_func = TruncDay
            elif period == 'week':
                start_date = end_date - timedelta(days=7)
                trunc_func = TruncDay
            else:  # day (24 часа)
                start_date = end_date - timedelta(days=1)
                trunc_func = TruncHour

            trades = Trade.objects.filter(exit_time__range=[start_date, end_date])
            grouped_data = trades.annotate(interval=trunc_func('exit_time')).values('interval').annotate(
                value=Sum('profit_loss')
            ).order_by('interval')

            result = [{'time': item['interval'].isoformat(), 'value': float(item['value'])} for item in grouped_data]
            return Response(result)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['GET'], url_path='balance-history')
    def balance_history(self, request):
        """Возвращает историю баланса с учетом периода."""
        try:
            period = request.query_params.get('period', 'day')
            end_date = timezone.now()

            # Определяем начальную дату на основе периода
            if period == 'year':
                start_date = end_date - timedelta(days=365)
            elif period == 'month':
                start_date = end_date - timedelta(days=30)
            elif period == 'week':
                start_date = end_date - timedelta(days=7)
            else:  # day (24 часа)
                start_date = end_date - timedelta(days=1)

            # Получаем позиции за период, используя entry_time
            positions = Position.objects.filter(entry_time__range=[start_date, end_date])

            # Группировка данных
            result = []
            grouped_positions = {}
            for position in positions:
                # Форматируем ключ: день или час в зависимости от периода
                key = position.entry_time.strftime('%Y-%m-%d %H' if period == 'day' else '%Y-%m-%d')
                if key not in grouped_positions:
                    grouped_positions[key] = 0
                grouped_positions[key] += position.current_value

            # Форматируем результат
            for key, value in sorted(grouped_positions.items()):
                result.append({
                    'time': key,
                    'value': float(value)
                })

            return Response(result)

        except Exception as e:
            logger.error(f"Error in balance_history: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer

    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        """Retourne les statistiques des trades"""
        period = request.query_params.get('period', '30d')

        if period == '30d':
            start_date = datetime.now() - timedelta(days=30)
        elif period == '7d':
            start_date = datetime.now() - timedelta(days=7)
        else:
            start_date = datetime.now() - timedelta(days=1)

        trades = self.queryset.filter(exit_time__gte=start_date)

        stats = {
            'total_trades': trades.count(),
            'winning_trades': trades.filter(profit_loss__gt=0).count(),
            'total_pnl': trades.aggregate(
                total_pnl=Sum('profit_loss')
            )['total_pnl'] or 0,
            'largest_win': trades.aggregate(
                max_win=Max('profit_loss')
            )['max_win'] or 0,
            'largest_loss': trades.aggregate(
                max_loss=Min('profit_loss')
            )['max_loss'] or 0
        }

        return Response(stats)


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        position = self.get_object()
        # Пример логики истории
        history = {"message": f"History for position {position.id}"}
        return Response(history)

    @action(detail=True, methods=['get'])
    def changes(self, request, pk=None):
        position = self.get_object()
        # Пример логики изменений
        changes = {"message": f"Changes for position {position.id}"}
        return Response(changes)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        position = self.get_object()
        position.status = "CLOSED"
        position.save()
        return Response({"status": "Position closed", "id": position.id})


class TradingDashboardViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['GET'])
    def portfolio_overview(self, request):
        """Retourne la vue d'ensemble du portfolio"""
        try:
            # Récupération des données de performance
            performance = self._calculate_performance_metrics()
            active_positions = self._get_active_positions()
            recent_trades = self._get_recent_trades()

            return Response({
                'performance': performance,
                'active_positions': active_positions,
                'recent_trades': recent_trades,
                'alerts': self._get_active_alerts()
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def strategy_performance(self, request):
        """Retourne les performances par stratégie"""
        try:
            strategies = TradingStrategy.objects.filter(is_active=True)
            strategy_metrics = []

            for strategy in strategies:
                trades = Trade.objects.filter(strategy=strategy)
                metrics = self._calculate_strategy_metrics(trades)
                strategy_metrics.append({
                    'id': strategy.id,
                    'name': strategy.name,
                    'metrics': metrics
                })

            return Response(strategy_metrics)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def trade_history(self, request):
        """Retourne l'historique des trades"""
        try:
            trades = Trade.objects.all().order_by('-entry_time')[:100]
            serialized_trades = TradeSerializer(trades, many=True).data

            return Response(serialized_trades)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['GET'])
    def risk_metrics(self, request):
        """Retourne les métriques de risque"""
        try:
            return Response({
                'portfolio_risk': self._calculate_portfolio_risk(),
                'strategy_risks': self._calculate_strategy_risks(),
                'market_risk': self._calculate_market_risk()
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _calculate_performance_metrics(self):
        """Calcule les métriques de performance"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        trades = Trade.objects.filter(
            exit_time__range=[start_date, end_date]
        )

        total_pnl = trades.aggregate(
            total_pnl=Sum('profit_loss')
        )['total_pnl'] or 0

        winning_trades = trades.filter(profit_loss__gt=0).count()
        total_trades = trades.count()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        return {
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'trade_count': total_trades,
            'average_trade': trades.aggregate(
                avg_trade=Avg('profit_loss')
            )['avg_trade'] or 0
        }

    def _calculate_strategy_metrics(self, trades):
        """Calcule les métriques pour une stratégie spécifique"""
        if not trades:
            return {}

        total_trades = trades.count()
        winning_trades = trades.filter(profit_loss__gt=0).count()

        return {
            'total_trades': total_trades,
            'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
            'total_pnl': trades.aggregate(total_pnl=Sum('profit_loss'))['total_pnl'] or 0,
            'average_trade': trades.aggregate(avg_trade=Avg('profit_loss'))['avg_trade'] or 0,
            'max_drawdown': self._calculate_max_drawdown(trades)
        }

    def _calculate_portfolio_risk(self):
        """Calcule les métriques de risque du portfolio"""
        active_positions = Position.objects.filter(status='OPEN')
        total_exposure = sum(position.current_value for position in active_positions)

        return {
            'total_exposure': total_exposure,
            'position_count': active_positions.count(),
            'risk_per_position': self._calculate_position_risks(active_positions),
            'correlation_risk': self._calculate_correlation_risk(),
            'var': self._calculate_value_at_risk()
        }

    def _calculate_market_risk(self):
        """Calcule les risques liés au marché"""
        # Implémenter le calcul des risques de marché
        pass


class ExchangeKeyViewSet(viewsets.ModelViewSet):
    serializer_class = ExchangeKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExchangeKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        exchange = serializer.validated_data['exchange']
        api_key = serializer.validated_data['api_key']
        api_secret = serializer.validated_data['api_secret']
        testnet = serializer.validated_data.get('testnet', False)

        is_valid, message = ExchangeFactory.verify_keys(
            exchange=exchange,
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )

        if not is_valid:
            raise serializers.ValidationError(message)

        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Проверка валидности ключей
        Returns:
            Response: Результат проверки с детальной информацией
        """
        exchange_key = self.get_object()

        try:
            result = {
                'status': 'checking',
                'api_key_valid': False,
                'has_trading_permission': False,
                'has_reading_permission': False,
                'testnet_status': None,
                'balances': None,
                'errors': []
            }

            # Проверяем ключи в зависимости от биржи
            if exchange_key.exchange == 'BINANCE':
                service = BinanceService(
                    api_key=exchange_key.api_key,
                    api_secret=exchange_key.api_secret,
                    testnet=exchange_key.testnet
                )

                try:
                    # Проверяем базовый доступ
                    is_valid, message = BinanceService.verify_credentials(
                        api_key=exchange_key.api_key,
                        api_secret=exchange_key.api_secret,
                        testnet=exchange_key.testnet
                    )
                    result['api_key_valid'] = is_valid
                    if not is_valid:
                        result['errors'].append(message)
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)

                    # Проверяем балансы
                    try:
                        balances = service.client.account()['balances']
                        non_zero_balances = [
                            b for b in balances
                            if Decimal(b['free']) > 0 or Decimal(b['locked']) > 0
                        ]
                        result['balances'] = non_zero_balances
                        result['has_reading_permission'] = True
                    except Exception as e:
                        result['errors'].append(f"Error checking balances: {str(e)}")

                    # Проверяем возможность торговли маленьким ордером
                    try:
                        # Проверяем возможность создания ордера без его реального размещения
                        service.client.new_order_test(
                            symbol='BTCUSDT',
                            side='BUY',
                            type='MARKET',
                            quoteOrderQty='10.1'  # Минимальный тестовый ордер
                        )
                        result['has_trading_permission'] = True
                    except Exception as e:
                        result['errors'].append(f"Error checking trading permission: {str(e)}")

                    # Обновляем время последней проверки
                    if result['api_key_valid']:
                        exchange_key.update_last_checked()

                    result['status'] = 'success' if not result['errors'] else 'partial_success'
                    return Response(result)

                except Exception as e:
                    result['errors'].append(str(e))
                    result['status'] = 'error'
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)

            return Response(
                {'error': 'Unsupported exchange'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def exchanges(self, request):
        """Возвращает список поддерживаемых бирж"""
        return Response([
            {'id': 'BINANCE', 'name': 'Binance'},
            {'id': 'BYBIT', 'name': 'Bybit'}
        ])