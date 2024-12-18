
# tasks/execute_trading_strategies.py
from celery import shared_task
from decimal import Decimal
from typing import Optional
from django.conf import settings
import logging

from ..models import TradingStrategy, Position, Trade
from ..services.binance_service import BinanceService
from ..services.exchange_factory import ExchangeFactory

logger = logging.getLogger(__name__)


class PositionManager:
    def __init__(self, exchange_service: BinanceService):
        self.exchange_service = exchange_service

    def open_position(self, strategy: TradingStrategy, current_price: Decimal) -> Optional[Position]:
        """Открытие новой позиции"""
        try:
            # Вычисляем размер позиции
            quantity = strategy.calculate_position_size()

            # Проверяем баланс
            required_balance = quantity * current_price
            available_balance = self.exchange_service.get_account_balance('USDT')

            if available_balance < required_balance:
                logger.warning(
                    f"Недостаточно средств для открытия позиции {strategy.symbol}. "
                    f"Требуется: {required_balance}, Доступно: {available_balance}"
                )
                return None

            # Размещаем ордер
            order = self.exchange_service.place_market_buy(
                symbol=strategy.symbol,
                quantity=quantity
            )

            # Создаем позицию в БД
            position = Position.objects.create(
                strategy=strategy,
                symbol=strategy.symbol,
                entry_price=Decimal(order['price']),
                quantity=Decimal(order['executedQty']),
                status='OPEN',
                order_id=order['orderId']
            )

            logger.info(f"Открыта новая позиция: {position}")
            return position

        except Exception as e:
            logger.error(f"Ошибка при открытии позиции {strategy.symbol}: {str(e)}")
            return None

    def close_position(self, position: Position, current_price: Decimal, reason: str) -> bool:
        """Закрытие позиции"""
        try:
            # Размещаем ордер на продажу
            order = self.exchange_service.place_market_sell(
                symbol=position.symbol,
                quantity=position.quantity
            )

            # Обновляем позицию
            position.status = 'CLOSED'
            position.exit_price = Decimal(order['price'])
            position.save()

            # Создаем запись о сделке
            Trade.objects.create(
                strategy=position.strategy,
                position=position,
                entry_price=position.entry_price,
                exit_price=position.exit_price,
                quantity=position.quantity,
                profit_loss=(position.exit_price - position.entry_price) * position.quantity,
                close_reason=reason
            )

            logger.info(f"Закрыта позиция: {position}, причина: {reason}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при закрытии позиции {position.id}: {str(e)}")
            return False


@shared_task
def execute_trading_strategies():
    """Выполнение торговых стратегий"""
    try:
        # Получаем сервис биржи через фабрику
        exchange_service = ExchangeFactory.get_service(
            exchange='BINANCE',
            api_key=settings.BINANCE_API_KEY,
            api_secret=settings.BINANCE_API_SECRET,
            testnet=settings.BINANCE_TESTNET
        )

        position_manager = PositionManager(exchange_service)
        active_strategies = TradingStrategy.objects.filter(is_active=True)

        for strategy in active_strategies:
            try:
                # Получаем текущую цену
                current_price = exchange_service.get_symbol_price(strategy.symbol)

                # Проверяем существующие позиции
                position = Position.objects.filter(
                    strategy=strategy,
                    status='OPEN'
                ).first()

                if position:
                    # Проверяем стоп-лосс и тейк-профит
                    price_change_percent = (
                            (current_price - position.entry_price) / position.entry_price * 100
                    )

                    if price_change_percent <= -strategy.stop_loss:
                        position_manager.close_position(
                            position, current_price, reason='stop_loss'
                        )
                    elif price_change_percent >= strategy.take_profit:
                        position_manager.close_position(
                            position, current_price, reason='take_profit'
                        )
                    # Проверяем сигнал на продажу от стратегии
                    elif strategy.should_sell(current_price):
                        position_manager.close_position(
                            position, current_price, reason='strategy_signal'
                        )

                else:
                    # Проверяем сигнал на покупку
                    if strategy.should_buy(current_price):
                        position_manager.open_position(strategy, current_price)

            except Exception as e:
                logger.error(f"Ошибка при обработке стратегии {strategy.id}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Критическая ошибка в execute_trading_strategies: {str(e)}")
        raise