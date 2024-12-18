
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Union, Dict, List
from dataclasses import dataclass

from .base import BaseIndicator, IndicatorResult


class OBV(BaseIndicator):
    def __init__(self, smooth_period: int = 20):
        super().__init__()
        self.smooth_period = smooth_period

    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        close = data['close']
        volume = data['volume']

        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        obv_ma = obv.rolling(window=self.smooth_period).mean()

        current_obv = obv.iloc[-1]
        current_ma = obv_ma.iloc[-1]

        signal = self.get_signal(
            current_obv,
            [obv.iloc[-2], current_ma]
        )

        divergence = self._check_divergence(data, obv)

        return IndicatorResult(
            value=current_obv,
            signal=signal,
            strength=self._calculate_signal_strength(current_obv, obv),
            additional_data={
                'obv_ma': current_ma,
                'divergence': divergence
            }
        )

    def get_signal(self, current_obv: float,
                   reference_values: List[float]) -> str:
        prev_obv, obv_ma = reference_values

        if current_obv > prev_obv and current_obv > obv_ma:
            return 'buy'
        elif current_obv < prev_obv and current_obv < obv_ma:
            return 'sell'
        return 'neutral'

    def _calculate_signal_strength(self, current_obv: float,
                                   obv_series: pd.Series) -> float:
        std_dev = obv_series.std()
        distance = abs(current_obv - obv_series.mean())
        return min(1.0, distance / (2 * std_dev))

    def _check_divergence(self, price_data: pd.DataFrame,
                          obv: pd.Series) -> str:
        # Vérification des divergences prix/volume
        price_trend = price_data['close'].iloc[-5:].pct_change().mean()
        obv_trend = obv.iloc[-5:].pct_change().mean()

        if price_trend > 0 and obv_trend < 0:
            return 'bearish'
        elif price_trend < 0 and obv_trend > 0:
            return 'bullish'
        return 'none'