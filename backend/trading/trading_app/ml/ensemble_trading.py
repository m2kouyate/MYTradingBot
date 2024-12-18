

from typing import Dict, List, Union

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
import joblib
import json

from .models import FeatureEngineering


logger = logging.getLogger(__name__)


@dataclass
class TradingSignal:
    timestamp: datetime
    symbol: str
    direction: str  # 'buy' or 'sell'
    confidence: float
    price: float
    models_agreement: float
    stop_loss: float
    take_profit: float


class EnsembleTradingSystem:
    def __init__(self,
                 ensemble_model: EnsembleModel,
                 confidence_threshold: float = 0.7,
                 min_model_agreement: float = 0.6):
        self.ensemble = ensemble_model
        self.confidence_threshold = confidence_threshold
        self.min_model_agreement = min_model_agreement
        self.signals_history = []
        self.performance_metrics = {}

    def generate_signals(self, market_data: pd.DataFrame) -> List[TradingSignal]:
        """Génère des signaux de trading basés sur l'ensemble des modèles"""
        try:
            # Préparation des données
            features = self._prepare_features(market_data)

            # Prédictions individuelles des modèles
            individual_predictions = self._get_individual_predictions(features)

            # Prédiction de l'ensemble
            ensemble_prediction = self.ensemble.predict(features)

            # Analyse de la concordance des modèles
            model_agreement = self._calculate_model_agreement(
                individual_predictions
            )

            # Génération des signaux
            signals = self._create_trading_signals(
                market_data,
                ensemble_prediction,
                model_agreement
            )

            # Mise à jour de l'historique
            self.signals_history.extend(signals)

            return signals

        except Exception as e:
            logging.error(f"Erreur lors de la génération des signaux: {str(e)}")
            return []

    def _prepare_features(self, market_data: pd.DataFrame) -> np.ndarray:
        """Prépare les features pour les prédictions"""
        feature_generator = FeatureEngineering()
        features = feature_generator.create_features(market_data)
        return features.values

    def _get_individual_predictions(self,
                                    features: np.ndarray) -> np.ndarray:
        """Obtient les prédictions de chaque modèle individuel"""
        predictions = []
        for model in self.ensemble.trained_models:
            pred = model.predict(features)
            predictions.append(pred)
        return np.array(predictions)

    def _calculate_model_agreement(self,
                                   predictions: np.ndarray) -> float:
        """Calcule le niveau d'accord entre les modèles"""
        # Conversion des prédictions en signaux directionnels
        signals = np.sign(np.diff(predictions, axis=1))

        # Calcul du pourcentage d'accord
        agreement = np.mean(
            np.abs(np.sum(signals, axis=0)) / len(self.ensemble.trained_models)
        )

        return agreement

    def _create_trading_signals(self,
                                market_data: pd.DataFrame,
                                predictions: np.ndarray,
                                model_agreement: float) -> List[TradingSignal]:
        """Crée les signaux de trading basés sur les prédictions"""
        signals = []
        current_price = market_data['close'].iloc[-1]

        # Calcul de la direction et de la confiance
        price_change = predictions[-1] - current_price
        direction = 'buy' if price_change > 0 else 'sell'
        confidence = self._calculate_signal_confidence(
            price_change,
            predictions,
            model_agreement
        )

        # Création du signal si la confiance est suffisante
        if (confidence > self.confidence_threshold and
                model_agreement > self.min_model_agreement):
            # Calcul des niveaux de stop-loss et take-profit
            stop_loss, take_profit = self._calculate_risk_levels(
                current_price,
                direction,
                market_data
            )

            signal = TradingSignal(
                timestamp=market_data.index[-1],
                symbol=market_data['symbol'].iloc[0],
                direction=direction,
                confidence=confidence,
                price=current_price,
                models_agreement=model_agreement,
                stop_loss=stop_loss,
                take_profit=take_profit
            )

            signals.append(signal)

        return signals

    def _calculate_signal_confidence(self,
                                     price_change: float,
                                     predictions: np.ndarray,
                                     model_agreement: float) -> float:
        """Calcule le niveau de confiance du signal"""
        # Normalisation du changement de prix
        normalized_change = abs(price_change) / predictions.std()

        # Combinaison des facteurs de confiance
        confidence = (
                0.4 * normalized_change +
                0.4 * model_agreement +
                0.2 * self.ensemble.weights.mean()
        )

        return min(confidence, 1.0)

    def _calculate_risk_levels(self,
                               current_price: float,
                               direction: str,
                               market_data: pd.DataFrame) -> Tuple[float, float]:
        """Calcule les niveaux de stop-loss et take-profit"""
        volatility = market_data['close'].pct_change().std()
        atr = self._calculate_atr(market_data)

        if direction == 'buy':
            stop_loss = current_price - 2 * atr
            take_profit = current_price + 3 * atr
        else:
            stop_loss = current_price + 2 * atr
            take_profit = current_price - 3 * atr

        return stop_loss, take_profit

    def _calculate_atr(self, market_data: pd.DataFrame,
                       period: int = 14) -> float:
        """Calcule l'Average True Range"""
        high = market_data['high']
        low = market_data['low']
        close = market_data['close']

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        return tr.rolling(window=period).mean().iloc[-1]

    def evaluate_performance(self, market_data: pd.DataFrame) -> Dict:
        """Évalue la performance du système"""
        if not self.signals_history:
            return {}

        # Conversion des signaux en DataFrame
        signals_df = pd.DataFrame([
            vars(signal) for signal in self.signals_history
        ])

        # Calcul des performances
        performance = self._calculate_trading_performance(
            signals_df,
            market_data
        )

        # Mise à jour des métriques
        self.performance_metrics = {
            'total_signals': len(signals_df),
            'win_rate': performance['win_rate'],
            'profit_factor': performance['profit_factor'],
            'sharpe_ratio': performance['sharpe_ratio'],
            'max_drawdown': performance['max_drawdown'],
            'average_profit': performance['average_profit'],
            'average_loss': performance['average_loss']
        }

        return self.performance_metrics

    def save_model(self, filepath: str):
        """Sauvegarde le modèle et ses configurations"""
        model_data = {
            'ensemble_model': self.ensemble,
            'confidence_threshold': self.confidence_threshold,
            'min_model_agreement': self.min_model_agreement,
            'performance_metrics': self.performance_metrics
        }

        joblib.dump(model_data, filepath)

    @classmethod
    def load_model(cls, filepath: str) -> 'EnsembleTradingSystem':
        """Charge un modèle sauvegardé"""
        model_data = joblib.load(filepath)

        system = cls(
            ensemble_model=model_data['ensemble_model'],
            confidence_threshold=model_data['confidence_threshold'],
            min_model_agreement=model_data['min_model_agreement']
        )

        system.performance_metrics = model_data['performance_metrics']

        return system