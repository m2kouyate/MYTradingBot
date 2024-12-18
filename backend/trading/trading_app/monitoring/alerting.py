
import asyncio
import random

from ..logging.advanced_logger import AdvancedLogger
from ..notifications.services import NotificationService


class AlertingSystem:
    def __init__(self, notification_service: NotificationService, logger: AdvancedLogger = None):
        self.notification_service = notification_service
        self.logger = logger or AdvancedLogger('alerting')

    async def monitor_system_health(self, max_cycles: int = None, interval: int = 60):
        """Мониторинг здоровья системы с ограничением по циклам и интервалом."""
        count = 0
        while max_cycles is None or count < max_cycles:
            try:
                await self._check_connections()
                await self._check_performance()
                await self._check_errors()

                count += 1
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.log_error(e, {'monitor': 'system_health'})
                break

    async def monitor_trading_activity(self, max_cycles: int = None, interval: int = 30):
        """Мониторинг активности торговли с ограничением по циклам и интервалом."""
        count = 0
        while max_cycles is None or count < max_cycles:
            try:
                await self._check_open_positions()
                await self._check_pending_orders()
                await self._check_trading_performance()

                count += 1
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.log_error(e, {'monitor': 'trading_activity'})
                break

    async def _check_connections(self):
        """Проверка соединений с внешними сервисами."""
        import random
        success = random.choice([True, False])
        if not success:
            message = "Connection to Binance API failed."
            self.logger.log_error(message)
            self.notification_service.send_notification("System Alert", message)
        else:
            self.logger.log_info("All connections are healthy.")

    async def _check_performance(self):
        """Проверка производительности системы."""
        performance = random.uniform(50, 100)  # Процент использования
        if performance > 90:
            message = f"High system load detected: {performance}%."
            self.logger.log_warning(message)
            self.notification_service.send_notification("Performance Alert", message)
        else:
            self.logger.log_info("System performance is within normal limits.")

    async def _check_errors(self):
        """Проверка на наличие ошибок в системе."""
        errors = random.randint(0, 5)
        if errors > 0:
            message = f"{errors} critical errors detected in logs."
            self.logger.log_error(message)
            self.notification_service.send_notification("Error Alert", message)
        else:
            self.logger.log_info("No errors detected in the system.")

    async def _check_open_positions(self):
        """Проверка открытых позиций в торговой системе."""
        positions = random.randint(0, 10)
        self.logger.log_info(f"{positions} open positions detected.")
        if positions > 8:
            message = f"High number of open positions: {positions}."
            self.logger.log_warning(message)
            self.notification_service.send_notification("Trading Alert", message)

    async def _check_pending_orders(self):
        """Проверка отложенных ордеров."""
        pending_orders = random.randint(0, 5)
        if pending_orders > 3:
            message = f"High number of pending orders: {pending_orders}."
            self.logger.log_warning(message)
            self.notification_service.send_notification("Pending Orders Alert", message)
        else:
            self.logger.log_info("Pending orders are within normal limits.")

    async def _check_trading_performance(self):
        """Проверка производительности торговых стратегий."""
        trade_success_rate = random.uniform(70, 100)
        self.logger.log_info(f"Current trade success rate: {trade_success_rate:.2f}%")
        if trade_success_rate < 80:
            message = f"Low trading performance detected: {trade_success_rate:.2f}% success rate."
            self.logger.log_warning(message)
            self.notification_service.send_notification("Trading Performance Alert", message)
