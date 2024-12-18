
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Union, Dict, List
from dataclasses import dataclass

from .base import BaseIndicator, IndicatorResult


class BollingerBands(BaseIndicator):
    def __init__(self, period: int = 20, num_std: float = 2.0):
        super().__init__()
        self.period = period
        self.num_std = num_std

    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        typical_price = (data['high'] + data['low'] + data['close']) / 3

        # Calcul des bandes
        middle_band = typical_price.rolling(window=self.period).mean()
        std_dev = typical_price.rolling(window=self.period).std()
        upper_band = middle_band + (std_dev * self.num_std)
        lower_band = middle_band - (std_dev * self.num_std)

        current_price = data['close'].iloc[-1]
        signal = self.get_signal(
            current_price,
            [upper_band.iloc[-1], middle_band.iloc[-1], lower_band.iloc[-1]]
        )

        # Calcul de la volatilité relative
        bandwidth = (upper_band - lower_band) / middle_band

        return IndicatorResult(
            value=middle_band.iloc[-1],
            signal=signal,
            strength=self._calculate_signal_strength(
                current_price,
                upper_band.iloc[-1],
                lower_band.iloc[-1]
            ),
            additional_data={
                'upper': upper_band.iloc[-1],
                'lower': lower_band.iloc[-1],
                'bandwidth': bandwidth.iloc[-1]
            }
        )

    def get_signal(self, current_price: float,
                   bands: List[float]) -> str:
        upper, middle, lower = bands

        if current_price > upper:
            return 'sell'
        elif current_price < lower:
            return 'buy'
        return 'neutral'

    def _calculate_signal_strength(self, price: float, upper: float,
                                   lower: float) -> float:
        band_range = upper - lower
        if price > upper:
            return min(1.0, (price - upper) / (band_range * 0.1))
        elif price < lower:
            return min(1.0, (lower - price) / (band_range * 0.1))
        return 0.0
