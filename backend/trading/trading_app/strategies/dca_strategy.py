
from decimal import Decimal
from datetime import datetime
from .base_strategy import BaseStrategy


class DCAStrategy(BaseStrategy):
    def __init__(self, binance_service, investment_amount: Decimal,
                 interval_days: int):
        super().__init__(binance_service)
        self.investment_amount = investment_amount
        self.interval_days = interval_days
        self.last_purchase = None

    def should_buy(self, symbol: str, current_price: Decimal) -> bool:
        if not self.last_purchase:
            return True

        time_since_last = datetime.now() - self.last_purchase
        return time_since_last.days >= self.interval_days

    def should_sell(self, symbol: str, current_price: Decimal) -> bool:
        return False  # DCA ne vend pas automatiquement

    def calculate_position_size(self, symbol: str) -> Decimal:
        current_price = Decimal(
            self.binance_service.client.get_symbol_ticker(symbol=symbol)['price']
        )
        return self.investment_amount / current_price