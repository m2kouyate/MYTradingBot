
# services/binance_service.py
from binance.spot import Spot as BinanceClient
from binance.exceptions import BinanceAPIException
from datetime import datetime
import logging
from decimal import Decimal
from typing import Dict, Optional, Tuple, List, Any

from .base_exchange_service import BaseExchangeService

logger = logging.getLogger(__name__)


class BinanceService(BaseExchangeService):
    BASE_URL = 'https://api.binance.com'
    TESTNET_URL = 'https://testnet.binance.vision'

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, testnet: bool = False):
        """
        Инициализация клиента Binance
        Args:
            api_key: API ключ
            api_secret: API секрет
            testnet: Использовать тестовую сеть
        """
        self.client = BinanceClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=self.TESTNET_URL if testnet else self.BASE_URL
        )

    @staticmethod
    def verify_credentials(api_key: str, api_secret: str, testnet: bool = False) -> Tuple[bool, str]:
        """
        Проверка API ключей
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            client = BinanceClient(
                api_key=api_key,
                api_secret=api_secret,
                base_url=BinanceService.TESTNET_URL if testnet else BinanceService.BASE_URL
            )
            # Проверяем разрешения ключей
            account = client.account()
            permissions = account.get('permissions', [])

            # Проверяем необходимые разрешения
            required_permissions = {'SPOT'}
            if not required_permissions.issubset(set(permissions)):
                return False, f"Недостаточно разрешений. Требуются: {required_permissions}"

            return True, "API ключи валидны"
        except BinanceAPIException as e:
            logger.error(f"Ошибка проверки API ключей Binance: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Неизвестная ошибка при проверке API ключей Binance: {str(e)}")
            return False, "Неизвестная ошибка при проверке ключей"

    def get_account_balance(self, asset: str) -> Decimal:
        """
        Получение баланса по конкретному активу
        Args:
            asset: Символ актива (например, 'BTC')
        Returns:
            Decimal: Доступный баланс
        """
        try:
            balance = self.client.account()['balances']
            asset_balance = next(
                (b for b in balance if b['asset'] == asset),
                None
            )
            if asset_balance is None:
                return Decimal('0')
            return Decimal(asset_balance['free'])
        except BinanceAPIException as e:
            logger.error(f"Ошибка при получении баланса {asset}: {str(e)}")
            raise

    def get_symbol_price(self, symbol: str) -> Decimal:
        """
        Получение текущей цены по символу
        Args:
            symbol: Торговая пара (например, 'BTCUSDT')
        Returns:
            Decimal: Текущая цена
        """
        try:
            ticker = self.client.ticker_price(symbol=symbol)
            return Decimal(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Ошибка при получении цены {symbol}: {str(e)}")
            raise

    def get_exchange_info(self) -> Dict:
        """
        Получение информации о бирже и торговых парах
        Returns:
            Dict: Информация о бирже
        """
        try:
            return self.client.exchange_info()
        except BinanceAPIException as e:
            logger.error(f"Ошибка при получении информации о бирже: {str(e)}")
            raise

    def place_market_buy(self, symbol: str, quantity: Decimal,
                         quote_order_qty: Optional[Decimal] = None) -> Dict:
        """
        Размещение рыночного ордера на покупку
        Args:
            symbol: Торговая пара
            quantity: Количество базового актива
            quote_order_qty: Количество котируемого актива (для покупки на определенную сумму)
        Returns:
            Dict: Информация об ордере
        """
        try:
            params = {
                'symbol': symbol,
                'side': 'BUY',
                'type': 'MARKET',
            }

            if quote_order_qty:
                params['quoteOrderQty'] = self._format_number(quote_order_qty)
            else:
                params['quantity'] = self._format_number(quantity)

            order = self.client.new_order(**params)
            logger.info(f"Создан ордер на покупку: {order}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Ошибка при создании ордера на покупку: {str(e)}")
            raise

    def place_market_sell(self, symbol: str, quantity: Decimal) -> Dict:
        """
        Размещение рыночного ордера на продажу
        Args:
            symbol: Торговая пара
            quantity: Количество базового актива
        Returns:
            Dict: Информация об ордере
        """
        try:
            order = self.client.new_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=self._format_number(quantity)
            )
            logger.info(f"Создан ордер на продажу: {order}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Ошибка при создании ордера на продажу: {str(e)}")
            raise

    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """
        Получение статуса ордера
        Args:
            symbol: Торговая пара
            order_id: ID ордера
        Returns:
            Dict: Информация об ордере
        """
        try:
            return self.client.get_order(symbol=symbol, orderId=order_id)
        except BinanceAPIException as e:
            logger.error(f"Ошибка при получении статуса ордера: {str(e)}")
            raise

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Получение открытых ордеров
        Args:
            symbol: Торговая пара (опционально)
        Returns:
            List[Dict]: Список открытых ордеров
        """
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
            return self.client.get_open_orders(**params)
        except BinanceAPIException as e:
            logger.error(f"Ошибка при получении открытых ордеров: {str(e)}")
            raise

    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """
        Отмена ордера
        Args:
            symbol: Торговая пара
            order_id: ID ордера
        Returns:
            Dict: Результат отмены
        """
        try:
            return self.client.cancel_order(symbol=symbol, orderId=order_id)
        except BinanceAPIException as e:
            logger.error(f"Ошибка при отмене ордера: {str(e)}")
            raise

    def get_klines(self, symbol: str, interval: str,
                   start_time: Optional[int] = None,
                   end_time: Optional[int] = None,
                   limit: Optional[int] = None) -> List[List[Any]]:
        """
        Получение исторических данных
        Args:
            symbol: Торговая пара
            interval: Интервал ('1m', '5m', '1h', '1d' и т.д.)
            start_time: Время начала в миллисекундах
            end_time: Время окончания в миллисекундах
            limit: Максимальное количество записей
        Returns:
            List[List]: Список свечей
        """
        try:
            params = {
                'symbol': symbol,
                'interval': interval
            }
            if start_time:
                params['startTime'] = start_time
            if end_time:
                params['endTime'] = end_time
            if limit:
                params['limit'] = limit

            return self.client.klines(**params)
        except BinanceAPIException as e:
            logger.error(f"Ошибка при получении исторических данных: {str(e)}")
            raise

    def get_ticker_24h(self, symbol: str) -> Dict:
        """
        Получение статистики за 24 часа
        Args:
            symbol: Торговая пара
        Returns:
            Dict: Статистика
        """
        try:
            return self.client.ticker_24hr(symbol=symbol)
        except BinanceAPIException as e:
            logger.error(f"Ошибка при получении 24ч статистики: {str(e)}")
            raise

    @staticmethod
    def _format_number(number: Decimal) -> str:
        """
        Форматирование числа для API
        Removes scientific notation and trailing zeros
        """
        return '{:f}'.format(number).rstrip('0').rstrip('.')