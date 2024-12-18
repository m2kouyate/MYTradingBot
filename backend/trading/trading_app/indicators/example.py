from typing import Dict
from typing import Dict
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

from backend.trading.trading_app.indicators.base import IndicatorResult
from backend.trading.trading_app.indicators.composite_analysis import CompositeAnalysis
from backend.trading.trading_app.indicators.momentum import MACD, RSI
from backend.trading.trading_app.indicators.trend import ADX
from backend.trading.trading_app.indicators.volatility import BollingerBands
from backend.trading.trading_app.indicators.volume import OBV


def create_trading_signals(data: pd.DataFrame) -> Dict:
    # Création des indicateurs
    indicators = {
        'RSI': RSI(period=14, oversold=30, overbought=70),
        'MACD': MACD(fast_period=12, slow_period=26, signal_period=9),
        'BollingerBands': BollingerBands(period=20, num_std=2.0),
        'ADX': ADX(period=14, threshold=25),
        'OBV': OBV(smooth_period=20)
    }

    # Analyse composite
    analyzer = CompositeAnalysis(indicators)
    results = analyzer.analyze(data)
    combined_signal = analyzer.get_combined_signal(results)

    # Construction du rapport détaillé
    detailed_analysis = {
        'combined_signal': combined_signal,
        'individual_signals': {
            name: {
                'signal': result.signal,
                'strength': result.strength,
                'value': result.value,
                'additional_data': result.additional_data
            }
            for name, result in results.items()
        },
        'market_context': analyze_market_context(data),
        'risk_assessment': assess_risk(results)
    }

    return detailed_analysis


def analyze_market_context(data: pd.DataFrame) -> Dict:
    """Analyse le contexte général du marché"""
    return {
        'trend': detect_market_trend(data),
        'volatility': calculate_market_volatility(data),
        'volume_analysis': analyze_volume_profile(data),
        'support_resistance': find_support_resistance_levels(data)
    }


def detect_market_trend(data: pd.DataFrame) -> Dict:
    """Détecte la tendance du marché en utilisant plusieurs timeframes"""
    closes = data['close']

    # Calcul des moyennes mobiles sur différentes périodes
    ma_20 = closes.rolling(window=20).mean()
    ma_50 = closes.rolling(window=50).mean()
    ma_200 = closes.rolling(window=200).mean()

    current_price = closes.iloc[-1]

    trend_status = {
        'short_term': 'bullish' if current_price > ma_20.iloc[-1] else 'bearish',
        'medium_term': 'bullish' if current_price > ma_50.iloc[-1] else 'bearish',
        'long_term': 'bullish' if current_price > ma_200.iloc[-1] else 'bearish'
    }

    # Force de la tendance
    trend_strength = {
        'short_term': abs(current_price - ma_20.iloc[-1]) / current_price,
        'medium_term': abs(current_price - ma_50.iloc[-1]) / current_price,
        'long_term': abs(current_price - ma_200.iloc[-1]) / current_price
    }

    return {
        'status': trend_status,
        'strength': trend_strength,
        'price_location': {
            'above_ma20': current_price > ma_20.iloc[-1],
            'above_ma50': current_price > ma_50.iloc[-1],
            'above_ma200': current_price > ma_200.iloc[-1]
        }
    }


def calculate_market_volatility(data: pd.DataFrame) -> Dict:
    """Calcule différentes mesures de volatilité"""
    returns = data['close'].pct_change()

    volatility = {
        'daily': returns.std() * np.sqrt(252),  # Annualisée
        'weekly': returns.rolling(window=5).std() * np.sqrt(52),
        'monthly': returns.rolling(window=21).std() * np.sqrt(12)
    }

    # Calcul de l'ATR (Average True Range)
    high = data['high']
    low = data['low']
    close = data['close']

    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=14).mean()

    return {
        'volatility_metrics': volatility,
        'atr': atr.iloc[-1],
        'atr_percentage': (atr.iloc[-1] / close.iloc[-1]) * 100,
        'volatility_regime': categorize_volatility(volatility['daily'])
    }


def analyze_volume_profile(data: pd.DataFrame) -> Dict:
    """Analyse le profil de volume"""
    volume = data['volume']
    price = data['close']

    # Volume moyen sur différentes périodes
    volume_ma = {
        'short_term': volume.rolling(window=5).mean().iloc[-1],
        'medium_term': volume.rolling(window=20).mean().iloc[-1],
        'long_term': volume.rolling(window=50).mean().iloc[-1]
    }

    # Ratio de volume actuel par rapport à la moyenne
    current_volume = volume.iloc[-1]
    volume_ratios = {
        period: current_volume / avg
        for period, avg in volume_ma.items()
    }

    # Analyse de la distribution du volume
    volume_price_correlation = volume.corr(price)

    return {
        'average_volumes': volume_ma,
        'volume_ratios': volume_ratios,
        'volume_trend': 'increasing' if volume_ratios['short_term'] > 1.5 else 'normal',
        'price_volume_correlation': volume_price_correlation
    }


def find_support_resistance_levels(data: pd.DataFrame,
                                   window: int = 20) -> Dict:
    """Identifie les niveaux de support et résistance"""
    highs = data['high'].rolling(window=window, center=True).max()
    lows = data['low'].rolling(window=window, center=True).min()

    # Identification des pivots
    pivot_high = (highs == data['high'])
    pivot_low = (lows == data['low'])

    resistance_levels = data.loc[pivot_high, 'high'].tail(3)
    support_levels = data.loc[pivot_low, 'low'].tail(3)

    current_price = data['close'].iloc[-1]

    return {
        'resistance_levels': resistance_levels.tolist(),
        'support_levels': support_levels.tolist(),
        'nearest_resistance': min(
            [r for r in resistance_levels if r > current_price],
            default=None
        ),
        'nearest_support': max(
            [s for s in support_levels if s < current_price],
            default=None
        )
    }


def assess_risk(indicator_results: Dict[str, IndicatorResult]) -> Dict:
    """Évalue le niveau de risque global"""
    risk_factors = {
        'indicator_divergence': check_indicator_divergence(indicator_results),
        'overbought_oversold': check_overbought_oversold(indicator_results),
        'trend_strength': assess_trend_strength(indicator_results),
        'volatility_risk': assess_volatility_risk(indicator_results)
    }

    # Calcul du score de risque global (0-100)
    risk_score = calculate_risk_score(risk_factors)

    return {
        'risk_score': risk_score,
        'risk_level': categorize_risk_level(risk_score),
        'risk_factors': risk_factors,
        'recommendations': generate_risk_recommendations(risk_factors)
    }


# Exemple d'utilisation dans une stratégie de trading
class EnhancedTradingStrategy:
    def __init__(self, config: Dict):
        self.config = config
        self.indicators = {
            'RSI': RSI(
                period=config.get('rsi_period', 14),
                oversold=config.get('rsi_oversold', 30),
                overbought=config.get('rsi_overbought', 70)
            ),
            'MACD': MACD(
                fast_period=config.get('macd_fast', 12),
                slow_period=config.get('macd_slow', 26),
                signal_period=config.get('macd_signal', 9)
            ),
            'BB': BollingerBands(
                period=config.get('bb_period', 20),
                num_std=config.get('bb_std', 2.0)
            )
        }
        self.analyzer = CompositeAnalysis(self.indicators)

    def analyze_market(self, data: pd.DataFrame) -> Dict:
        """Analyse complète du marché"""
        analysis = create_trading_signals(data)
        risk_assessment = assess_risk(analysis['individual_signals'])

        # Ajout du contexte de marché
        market_context = analyze_market_context(data)

        return {
            'signals': analysis,
            'risk': risk_assessment,
            'context': market_context,
            'recommendation': self.generate_trading_recommendation(
                analysis,
                risk_assessment,
                market_context
            )
        }

    def generate_trading_recommendation(self, signals: Dict,
                                        risk: Dict,
                                        context: Dict) -> Dict:
        """Génère une recommandation de trading basée sur l'analyse complète"""
        combined_signal = signals['combined_signal']

        # Ajustement de la taille de position en fonction du risque
        position_size = self.calculate_position_size(
            risk['risk_score'],
            context['volatility']['atr_percentage']
        )

        return {
            'action': combined_signal['signal'],
            'confidence': combined_signal['strength'],
            'position_size': position_size,
            'stop_loss': self.calculate_stop_loss(
                context['support_resistance'],
                context['volatility']
            ),
            'take_profit': self.calculate_take_profit(
                context['support_resistance'],
                combined_signal['strength']
            ),
            'timeframe': self.determine_optimal_timeframe(context['trend'])
        }