
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Union, Dict, List
from dataclasses import dataclass

from .base import BaseIndicator, IndicatorResult


class RSI(BaseIndicator):
    def __init__(self, period: int = 14, oversold: float = 30,
                 overbought: float = 70):
        super().__init__()
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        close_delta = data['close'].diff()

        # Calcul des gains et pertes
        gain = (close_delta.where(close_delta > 0, 0)).rolling(
            window=self.period
        ).mean()
        loss = (-close_delta.where(close_delta < 0, 0)).rolling(
            window=self.period
        ).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]

        # Détermination du signal et de la force
        signal = self.get_signal(current_rsi, rsi.iloc[-5:].tolist())
        strength = self._calculate_signal_strength(current_rsi)

        return IndicatorResult(
            value=current_rsi,
            signal=signal,
            strength=strength,
            additional_data={'rsi_values': rsi.tail(10).tolist()}
        )

    def get_signal(self, current_value: float,
                   previous_values: List[float]) -> str:
        if current_value < self.oversold:
            return 'buy'
        elif current_value > self.overbought:
            return 'sell'
        return 'neutral'

    def _calculate_signal_strength(self, rsi_value: float) -> float:
        if rsi_value <= self.oversold:
            return min(1.0, (self.oversold - rsi_value) / 10)
        elif rsi_value >= self.overbought:
            return min(1.0, (rsi_value - self.overbought) / 10)
        return 0.0


class MACD(BaseIndicator):
    def __init__(self, fast_period: int = 12, slow_period: int = 26,
                 signal_period: int = 9):
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        # Calcul des moyennes mobiles exponentielles
        fast_ema = data['close'].ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = data['close'].ewm(span=self.slow_period, adjust=False).mean()

        # Calcul du MACD et de sa ligne de signal
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        histogram = macd_line - signal_line

        current_hist = histogram.iloc[-1]
        signal = self.get_signal(current_hist, histogram.iloc[-5:].tolist())
        strength = self._calculate_signal_strength(current_hist, histogram)

        return IndicatorResult(
            value=current_hist,
            signal=signal,
            strength=strength,
            additional_data={
                'macd_line': macd_line.iloc[-1],
                'signal_line': signal_line.iloc[-1],
                'histogram': current_hist
            }
        )

    def get_signal(self, current_value: float,
                   previous_values: List[float]) -> str:
        if len(previous_values) < 2:
            return 'neutral'

        # Détecter un croisement
        if previous_values[-2] < 0 and current_value > 0:
            return 'buy'
        elif previous_values[-2] > 0 and current_value < 0:
            return 'sell'
        return 'neutral'

    def _calculate_signal_strength(self, current_hist: float,
                                   histogram: pd.Series) -> float:
        avg_hist = abs(histogram.mean())
        return min(1.0, abs(current_hist) / (2 * avg_hist))
