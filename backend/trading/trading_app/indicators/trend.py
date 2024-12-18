
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Union, Dict, List
from dataclasses import dataclass

from .base import BaseIndicator, IndicatorResult


class ADX(BaseIndicator):
    def __init__(self, period: int = 14, threshold: int = 25):
        super().__init__()
        self.period = period
        self.threshold = threshold

    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        high = data['high']
        low = data['low']
        close = data['close']

        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.period).mean()

        # Directional Movement
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low

        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

        plus_di = 100 * pd.Series(plus_dm).rolling(
            window=self.period
        ).mean() / atr
        minus_di = 100 * pd.Series(minus_dm).rolling(
            window=self.period
        ).mean() / atr

        # ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=self.period).mean()

        current_adx = adx.iloc[-1]
        current_plus_di = plus_di.iloc[-1]
        current_minus_di = minus_di.iloc[-1]

        signal = self.get_signal(
            current_adx,
            [current_plus_di, current_minus_di]
        )

        return IndicatorResult(
            value=current_adx,
            signal=signal,
            strength=self._calculate_signal_strength(current_adx),
            additional_data={
                'plus_di': current_plus_di,
                'minus_di': current_minus_di
            }
        )

    def get_signal(self, adx: float, di_values: List[float]) -> str:
        plus_di, minus_di = di_values

        if adx > self.threshold:
            if plus_di > minus_di:
                return 'buy'
            elif minus_di > plus_di:
                return 'sell'
        return 'neutral'

    def _calculate_signal_strength(self, adx: float) -> float:
        return min(1.0, (adx - self.threshold) / 30) if adx > self.threshold else 0.0
