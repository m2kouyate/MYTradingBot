
from typing import Dict
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Union, Dict, List
from dataclasses import dataclass

from .base import BaseIndicator, IndicatorResult


class CompositeAnalysis:
    def __init__(self, indicators: Dict[str, BaseIndicator]):
        self.indicators = indicators

    def analyze(self, data: pd.DataFrame) -> Dict[str, IndicatorResult]:
        results = {}
        for name, indicator in self.indicators.items():
            results[name] = indicator.calculate(data)
        return results

    def get_combined_signal(self, results: Dict[str, IndicatorResult]) -> Dict:
        total_strength = 0
        weighted_signal = 0

        # Poids des indicateurs
        weights = {
            'RSI': 0.2,
            'MACD': 0.25,
            'BollingerBands': 0.2,
            'ADX': 0.2,
            'OBV': 0.15
        }

        for name, result in results.items():
            if name not in weights:
                continue

            signal_value = {
                'buy': 1,
                'sell': -1,
                'neutral': 0
            }[result.signal]

            weight = weights[name]
            weighted_signal += signal_value * result.strength * weight
            total_strength += result.strength * weight

        if total_strength == 0:
            return {
                'signal': 'neutral',
                'strength': 0,
                'confidence': 0
            }

        normalized_signal = weighted_signal / total_strength

        # Détermination du signal final
        if normalized_signal > 0.3:
            final_signal = 'buy'
        elif normalized_signal < -0.3:
            final_signal = 'sell'
        else:
            final_signal = 'neutral'

        return {
            'signal': final_signal,
            'strength': abs(normalized_signal),
            'confidence': total_strength
        }


