

from typing import Dict, List, Union, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import tensorflow as tf
from xgboost import XGBRegressor, XGBClassifier
import lightgbm as lgb
from datetime import datetime, timedelta
import joblib


class FeatureEngineering:
    def __init__(self, lookback_periods: List[int] = [5, 10, 20, 50]):
        self.lookback_periods = lookback_periods
        self.scaler = StandardScaler()

    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Crée les features pour le machine learning"""
        df = data.copy()

        # Features techniques
        for period in self.lookback_periods:
            # Moyennes mobiles
            df[f'sma_{period}'] = df['close'].rolling(period).mean()
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()

            # Volatilité
            df[f'volatility_{period}'] = df['close'].rolling(period).std()

            # Momentum
            df[f'roc_{period}'] = df['close'].pct_change(period)

            # Volume
            df[f'volume_sma_{period}'] = df['volume'].rolling(period).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

        # Bandes de Bollinger
        df['bb_middle'] = df['close'].rolling(20).mean()
        df['bb_upper'] = df['bb_middle'] + 2 * df['close'].rolling(20).std()
        df['bb_lower'] = df['bb_middle'] - 2 * df['close'].rolling(20).std()

        return df

    def prepare_ml_data(self,
                        data: pd.DataFrame,
                        target_column: str,
                        prediction_horizon: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """Prépare les données pour le machine learning"""
        # Création des features
        df = self.create_features(data)

        # Création de la variable cible
        df['target'] = df[target_column].shift(-prediction_horizon)

        # Suppression des lignes avec des NaN
        df = df.dropna()

        # Sélection des features
        feature_columns = [col for col in df.columns if col not in
                           ['target', 'open', 'high', 'low', 'close', 'volume']]

        X = df[feature_columns].values
        y = df['target'].values

        # Normalisation
        X = self.scaler.fit_transform(X)

        return X, y


class MLModel:
    def __init__(self, model_type: str = 'lstm'):
        self.model_type = model_type
        self.model = None
        self.feature_engineering = FeatureEngineering()

    def create_model(self, input_shape: int):
        """Crée le modèle ML selon le type spécifié"""
        if self.model_type == 'lstm':
            self.model = tf.keras.Sequential([
                tf.keras.layers.LSTM(50, input_shape=(input_shape, 1),
                                     return_sequences=True),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.LSTM(50, return_sequences=False),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(25),
                tf.keras.layers.Dense(1)
            ])
            self.model.compile(optimizer='adam', loss='mse')

        elif self.model_type == 'xgboost':
            self.model = XGBRegressor(
                objective='reg:squarederror',
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5
            )

        elif self.model_type == 'lightgbm':
            self.model = lgb.LGBMRegressor(
                objective='regression',
                n_estimators=100,
                learning_rate=0.1
            )

    def train(self, X: np.ndarray, y: np.ndarray,
              validation_split: float = 0.2):
        """Entraîne le modèle"""
        if self.model_type == 'lstm':
            X = X.reshape((X.shape[0], X.shape[1], 1))
            self.model.fit(
                X, y,
                epochs=50,
                batch_size=32,
                validation_split=validation_split,
                verbose=1
            )
        else:
            # Pour XGBoost et LightGBM
            self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Fait des prédictions"""
        if self.model_type == 'lstm':
            X = X.reshape((X.shape[0], X.shape[1], 1))
        return self.model.predict(X)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Évalue les performances du modèle"""
        predictions = self.predict(X)

        # Pour la classification
        if self.model_type in ['xgboost_classifier', 'lightgbm_classifier']:
            return {
                'accuracy': accuracy_score(y, predictions),
                'precision': precision_score(y, predictions),
                'recall': recall_score(y, predictions),
                'f1': f1_score(y, predictions)
            }

        # Pour la régression
        return {
            'mse': np.mean((y - predictions) ** 2),
            'rmse': np.sqrt(np.mean((y - predictions) ** 2)),
            'mae': np.mean(np.abs(y - predictions))
        }


class MLBacktester:
    def __init__(self, data: pd.DataFrame, model: MLModel):
        self.data = data
        self.model = model
        self.results = None

    def run_backtest(self,
                     initial_capital: float = 10000.0,
                     position_size: float = 0.1):
        """Exécute le backtest avec le modèle ML"""
        df = self.data.copy()

        # Préparation des données
        X, y = self.model.feature_engineering.prepare_ml_data(df, 'close')

        # Split train/test
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        # Entraînement du modèle
        self.model.create_model(X_train.shape[1])
        self.model.train(X_train, y_train)

        # Prédictions sur l'ensemble de test
        predictions = self.model.predict(X_test)

        # Simulation de trading
        portfolio_value = initial_capital
        positions = []
        trades = []

        for i in range(len(predictions) - 1):
            current_price = df['close'].iloc[train_size + i]
            predicted_price = predictions[i]

            # Logique de trading
            if predicted_price > current_price * 1.01:  # Signal d'achat
                if not positions:  # Si pas de position ouverte
                    position_size_usd = portfolio_value * position_size
                    quantity = position_size_usd / current_price
                    positions.append({
                        'entry_price': current_price,
                        'quantity': quantity,
                        'entry_time': df.index[train_size + i]
                    })
                    trades.append({
                        'type': 'buy',
                        'price': current_price,
                        'quantity': quantity,
                        'time': df.index[train_size + i]
                    })

            elif predicted_price < current_price * 0.99:  # Signal de vente
                if positions:  # Si position ouverte
                    position = positions.pop()
                    pnl = (current_price - position['entry_price']) * position['quantity']
                    portfolio_value += pnl
                    trades.append({
                        'type': 'sell',
                        'price': current_price,
                        'quantity': position['quantity'],
                        'time': df.index[train_size + i],
                        'pnl': pnl
                    })

        # Calcul des résultats
        self.results = {
            'trades': pd.DataFrame(trades),
            'final_portfolio_value': portfolio_value,
            'total_return': (portfolio_value - initial_capital) / initial_capital * 100,
            'model_metrics': self.model.evaluate(X_test, y_test)
        }

        return self.results


class BacktestVisualizer:
    def __init__(self, backtest_results: Dict):
        self.results = backtest_results

    def create_performance_chart(self) -> go.Figure:
        """Crée un graphique de performance"""
        trades_df = self.results['trades']

        fig = go.Figure()

        # Ajout des trades
        fig.add_trace(go.Scatter(
            x=trades_df['time'],
            y=trades_df['price'],
            mode='markers',
            marker=dict(
                size=10,
                color=trades_df['type'].map({
                    'buy': 'green',
                    'sell': 'red'
                })
            ),
            name='Trades'
        ))

        # Ajout de la courbe de prix
        fig.add_trace(go.Scatter(
            x=trades_df['time'],
            y=trades_df['price'],
            mode='lines',
            name='Price'
        ))

        return fig

    def create_metrics_dashboard(self) -> Dict[str, go.Figure]:
        """Crée un dashboard des métriques"""
        dashboard = {}

        # Distribution des returns
        returns = self.results['trades']['pnl'].dropna()
        dashboard['returns_dist'] = go.Figure(data=[
            go.Histogram(x=returns, nbinsx=50)
        ])

        # Courbe de capital
        cumulative_returns = returns.cumsum()
        dashboard['equity_curve'] = go.Figure(data=[
            go.Scatter(x=cumulative_returns.index, y=cumulative_returns.values)
        ])

        return dashboard