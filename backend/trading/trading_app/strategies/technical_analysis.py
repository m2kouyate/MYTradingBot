
from decimal import Decimal
import numpy as np
import pandas as pd
from typing import List, Dict


class TechnicalAnalysis:
    def __init__(self, binance_service):
        self.binance_service = binance_service

    def get_historical_data(self, symbol: str, interval: str,
                            limit: int = 100) -> pd.DataFrame:
        """Récupère les données historiques et calcule les indicateurs"""
        klines = self.binance_service.client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close',
            'volume', 'close_time', 'quote_asset_volume',
            'number_of_trades', 'taker_buy_base_asset_volume',
            'taker_buy_quote_asset_volume', 'ignore'
        ])

        df['close'] = pd.to_numeric(df['close'])
        return df

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calcule le RSI (Relative Strength Index)"""
        if data.empty or len(data) < period:
            raise ValueError("Insufficient data for calculation.")

        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def calculate_macd(self, data: pd.DataFrame, return_series: bool = False) -> Dict[str, float]:
        exp1 = data['close'].ewm(span=12, adjust=False).mean()
        exp2 = data['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()

        if return_series:
            return {'macd_series': macd, 'signal_series': signal}

        return {
            'macd': macd.iloc[-1],
            'signal': signal.iloc[-1],
            'histogram': macd.iloc[-1] - signal.iloc[-1]
        }