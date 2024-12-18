
from decimal import Decimal
from typing import Dict, Optional

import pandas as pd

from .base_strategy import BaseStrategy
from .technical_analysis import TechnicalAnalysis
import logging

logger = logging.getLogger(__name__)


class AdvancedStrategy(BaseStrategy):
    def __init__(self, binance_service, config: Dict):
        super().__init__(binance_service)
        self.config = config
        self.ta = TechnicalAnalysis(binance_service)

        # Configuration des seuils
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.stop_loss_pct = config.get('stop_loss_pct', 5)
        self.take_profit_pct = config.get('take_profit_pct', 10)
        self.max_position_size = config.get('max_position_size', 0.1)

    def should_buy(self, symbol: str, current_price: Decimal) -> bool:
        try:
            # Récupération des données historiques
            hist_data = self.ta.get_historical_data(symbol, '1h')

            # Calcul des indicateurs
            rsi = self.ta.calculate_rsi(hist_data)
            macd = self.ta.calculate_macd(hist_data)

            # Logique d'achat combinant plusieurs indicateurs
            buy_signals = [
                rsi < self.rsi_oversold,  # RSI en survente
                macd['histogram'] > 0,  # MACD positif
                self._check_volume_trend(hist_data),  # Volume croissant
                self._check_market_trend(hist_data)  # Tendance haussière
            ]

            return all(buy_signals)

        except Exception as e:
            logger.error(f"Erreur dans l'analyse d'achat: {str(e)}")
            return False

    def should_sell(self, symbol: str, current_price: Decimal, entry_price: Optional[Decimal] = None) -> bool:
        try:
            if entry_price is None:
                logger.error("Entry price is required for 'should_sell'.")
                return False

            # Calcul des pourcentages de profit/perte
            price_change_pct = ((current_price - entry_price) / entry_price) * 100

            # Vérification des conditions de stop-loss et take-profit
            if price_change_pct <= -self.stop_loss_pct:
                logger.info(f"Stop-loss déclenché à {price_change_pct}%")
                return True

            if price_change_pct >= self.take_profit_pct:
                logger.info(f"Take-profit déclenché à {price_change_pct}%")
                return True

            # Analyse technique pour la sortie
            hist_data = self.ta.get_historical_data(symbol, '1h')
            rsi = self.ta.calculate_rsi(hist_data)
            macd = self.ta.calculate_macd(hist_data)

            sell_signals = [
                rsi > self.rsi_overbought,  # RSI en surachat
                macd['histogram'] < 0,  # MACD négatif
                self._check_reversal_pattern(hist_data)  # Pattern de renversement
            ]

            return any(sell_signals)

        except Exception as e:
            logger.error(f"Erreur dans l'analyse de vente: {str(e)}")
            return False

    @staticmethod
    def _check_volume_trend(data: pd.DataFrame) -> bool:
        """Vérifie si le volume est en augmentation"""
        recent_volume = data['volume'].tail(5).mean()
        previous_volume = data['volume'].tail(10).head(5).mean()
        return recent_volume > previous_volume

    @staticmethod
    def _check_market_trend(data: pd.DataFrame) -> bool:
        """Détermine la tendance du marché"""
        sma_20 = data['close'].rolling(window=20).mean()
        sma_50 = data['close'].rolling(window=50).mean()
        return sma_20.iloc[-1] > sma_50.iloc[-1]

    @staticmethod
    def _check_reversal_pattern(data: pd.DataFrame) -> bool:
        """Détecte les patterns de renversement"""
        # Implémentation basique - à enrichir selon vos besoins
        last_candles = data.tail(3)
        return (last_candles['high'].is_monotonic_decreasing and
                last_candles['low'].is_monotonic_decreasing)


