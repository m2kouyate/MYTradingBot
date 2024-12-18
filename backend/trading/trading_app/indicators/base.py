
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Union, Dict, List
from dataclasses import dataclass


@dataclass
class IndicatorResult:
    value: float
    signal: str  # 'buy', 'sell', or 'neutral'
    strength: float  # 0 to 1
    additional_data: Dict = None


class BaseIndicator(ABC):
    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        """Calcule la valeur de l'indicateur"""
        pass

    @abstractmethod
    def get_signal(self, current_value: float, previous_values: List[float]) -> str:
        """Détermine le signal de trading basé sur l'indicateur"""
        pass