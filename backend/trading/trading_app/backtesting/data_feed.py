
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from binance.client import Client


class HistoricalDataFeed:
    def __init__(self, binance_service):
        self.binance_service = binance_service
        self.data_cache = {}

    def get_historical_data(
            self,
            symbol: str,
            start_time: datetime,
            end_time: datetime,
            interval: str = Client.KLINE_INTERVAL_1HOUR
    ) -> pd.DataFrame:
        """
        Récupère les données historiques de Binance et les met en cache
        """
        cache_key = f"{symbol}_{interval}_{start_time.date()}_{end_time.date()}"

        if cache_key in self.data_cache:
            return self.data_cache[cache_key]

        klines = self.binance_service.client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=start_time.strftime('%Y-%m-%d'),
            end_str=end_time.strftime('%Y-%m-%d')
        )

        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades_count',
            'taker_buy_volume', 'taker_buy_quote_volume', 'ignored'
        ])

        # Conversion des types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.set_index('timestamp', inplace=True)
        self.data_cache[cache_key] = df

        return df