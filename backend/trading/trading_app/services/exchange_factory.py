
# services/exchange_factory.py
from typing import Optional, Type, Tuple
from .base_exchange_service import BaseExchangeService
from .binance_service import BinanceService
from .bybit_service import BybitService


class ExchangeFactory:
    _services = {
        'BINANCE': BinanceService,
        'BYBIT': BybitService
    }

    @classmethod
    def get_service(cls, exchange: str, api_key: Optional[str] = None,
                    api_secret: Optional[str] = None, testnet: bool = False) -> BaseExchangeService:
        if exchange not in cls._services:
            raise ValueError(f"Unsupported exchange: {exchange}")

        service_class = cls._services[exchange]
        return service_class(api_key=api_key, api_secret=api_secret, testnet=testnet)

    @classmethod
    def verify_keys(cls, exchange: str, api_key: str, api_secret: str, testnet: bool = False) -> Tuple[bool, str]:
        if exchange not in cls._services:
            return False, "Unsupported exchange"

        service_class = cls._services[exchange]
        return service_class.verify_credentials(api_key, api_secret, testnet)