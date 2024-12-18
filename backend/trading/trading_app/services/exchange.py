
# services/exchange.py
from binance.spot import Spot as BinanceClient
from pybit.unified_trading import HTTP as BybitClient
import hmac
import hashlib
import time

class ExchangeService:
    @staticmethod
    def verify_binance_keys(api_key: str, api_secret: str, testnet: bool = False) -> bool:
        try:
            client = BinanceClient(
                api_key=api_key,
                api_secret=api_secret,
                base_url='https://testnet.binance.vision' if testnet else 'https://api.binance.com'
            )
            # Проверяем баланс аккаунта для верификации ключей
            account_info = client.account()
            return True
        except Exception as e:
            print(f"Binance key verification error: {str(e)}")
            return False

    @staticmethod
    def verify_bybit_keys(api_key: str, api_secret: str, testnet: bool = False) -> bool:
        try:
            client = BybitClient(
                testnet=testnet,
                api_key=api_key,
                api_secret=api_secret
            )
            # Проверяем баланс аккаунта для верификации ключей
            wallet_balance = client.get_wallet_balance()
            return True
        except Exception as e:
            print(f"Bybit key verification error: {str(e)}")
            return False


