
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Optional


class BaseStrategy(ABC):
    def __init__(self, binance_service):
        self.binance_service = binance_service

    def should_buy(self, symbol: str, current_price: Decimal) -> bool:
        raise NotImplementedError

    def should_sell(self, symbol: str, current_price: Decimal) -> bool:
        raise NotImplementedError

    @abstractmethod
    def calculate_position_size(self, symbol: str) -> Decimal:
        pass