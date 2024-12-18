
# services/base_exchange_service.py
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
from decimal import Decimal


class BaseExchangeService(ABC):
    @staticmethod
    @abstractmethod
    def verify_credentials(api_key: str, api_secret: str, testnet: bool = False) -> Tuple[bool, str]:
        """Verify API key and secret"""
        pass

    @abstractmethod
    def get_account_balance(self, asset: str) -> Decimal:
        """Get balance for specific asset"""
        pass

    @abstractmethod
    def get_symbol_price(self, symbol: str) -> Decimal:
        """Get current price for symbol"""
        pass

    @abstractmethod
    def place_market_buy(self, symbol: str, quantity: Decimal) -> Dict:
        """Place market buy order"""
        pass

    @abstractmethod
    def place_market_sell(self, symbol: str, quantity: Decimal) -> Dict:
        """Place market sell order"""
        pass

    @abstractmethod
    def get_exchange_info(self) -> Dict:
        """Get exchange information"""
        pass