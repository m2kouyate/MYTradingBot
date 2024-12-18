

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from bayes_opt import BayesianOptimization
from functools import partial
import optuna
import lightgbm as lgb
import xgboost as xgb
import tensorflow as tf
from dataclasses import dataclass
import joblib


@dataclass
class OptimizationConfig:
    n_trials: int = 100
    cv_folds: int = 5
    early_stopping_rounds: int = 50
    optimization_metric: str = 'sharpe_ratio'
    random_seed: int = 42


class HyperparameterOptimizer:
    def __init__(self,
                 model_type: str,
                 config: OptimizationConfig):
        self.model_type = model_type
        self.config = config
        self.best_params = None
        self.optimization_history = []

    def optimize(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Optimise les hyperparamètres du modèle"""
        study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=self.config.random_seed)
        )

        # Définition de l'espace de recherche selon le type de modèle
        if self.model_type == 'lightgbm':
            objective = partial(
                self._objective_lightgbm,
                X=X, y=y
            )
        elif self.model_type == 'xgboost':
            objective = partial(
                self._objective_xgboost,
                X=X, y=y
            )
        elif self.model_type == 'lstm':
            objective = partial(
                self._objective_lstm,
                X=X, y=y
            )

        # Lancement de l'optimisation
        study.optimize(
            objective,
            n_trials=self.config.n_trials,
            show_progress_bar=True
        )

        self.best_params = study.best_params
        self.optimization_history = study.trials_dataframe()

        return {
            'best_params': self.best_params,
            'best_score': study.best_value,
            'optimization_history': self.optimization_history
        }

    def _objective_lightgbm(self,
                            trial: optuna.Trial,
                            X: np.ndarray,
                            y: np.ndarray) -> float:
        """Fonction objectif pour LightGBM"""
        param = {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'num_leaves': trial.suggest_int('num_leaves', 20, 3000),
            'learning_rate': trial.suggest_loguniform('learning_rate', 0.005, 0.05),
            'feature_fraction': trial.suggest_uniform('feature_fraction', 0.4, 1.0),
            'bagging_fraction': trial.suggest_uniform('bagging_fraction', 0.4, 1.0),
            'bagging_freq': trial.suggest_int('bagging_freq', 1, 7),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'min_child_samples': trial.suggest_int('min_child_samples', 5, 100),
            'lambda_l1': trial.suggest_loguniform('lambda_l1', 1e-8, 10.0),
            'lambda_l2': trial.suggest_loguniform('lambda_l2', 1e-8, 10.0)
        }

        scores = []
        tscv = TimeSeriesSplit(n_splits=self.config.cv_folds)

        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            train_data = lgb.Dataset(X_train, label=y_train)
            val_data = lgb.Dataset(X_val, label=y_val)

            model = lgb.train(
                param,
                train_data,
                valid_sets=[val_data],
                num_boost_round=10000,
                early_stopping_rounds=self.config.early_stopping_rounds,
                verbose_eval=False
            )

            pred = model.predict(X_val)
            score = self._calculate_metric(y_val, pred)
            scores.append(score)

        return np.mean(scores)

    def _objective_xgboost(self,
                           trial: optuna.Trial,
                           X: np.ndarray,
                           y: np.ndarray) -> float:
        """Fonction objectif pour XGBoost"""
        param = {
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'learning_rate': trial.suggest_loguniform('learning_rate', 0.005, 0.05),
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
            'gamma': trial.suggest_loguniform('gamma', 1e-8, 1.0),
            'subsample': trial.suggest_uniform('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_uniform('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_loguniform('reg_alpha', 1e-8, 10.0),
            'reg_lambda': trial.suggest_loguniform('reg_lambda', 1e-8, 10.0)
        }

        scores = []
        tscv = TimeSeriesSplit(n_splits=self.config.cv_folds)

        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            model = xgb.XGBRegressor(**param)
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                early_stopping_rounds=self.config.early_stopping_rounds,
                verbose=False
            )

            pred = model.predict(X_val)
            score = self._calculate_metric(y_val, pred)
            scores.append(score)

        return np.mean(scores)

    def _objective_lstm(self,
                        trial: optuna.Trial,
                        X: np.ndarray,
                        y: np.ndarray) -> float:
        """Fonction objectif pour LSTM"""
        param = {
            'units_l1': trial.suggest_int('units_l1', 32, 256),
            'units_l2': trial.suggest_int('units_l2', 16, 128),
            'dropout1': trial.suggest_uniform('dropout1', 0.1, 0.5),
            'dropout2': trial.suggest_uniform('dropout2', 0.1, 0.5),
            'optimizer_learning_rate': trial.suggest_loguniform(
                'optimizer_learning_rate',
                1e-5, 1e-2
            )
        }

        scores = []
        tscv = TimeSeriesSplit(n_splits=self.config.cv_folds)

        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            model = self._create_lstm_model(param)

            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=100,
                batch_size=32,
                callbacks=[
                    tf.keras.callbacks.EarlyStopping(
                        patience=self.config.early_stopping_rounds,
                        restore_best_weights=True
                    )
                ],
                verbose=0
            )

            pred = model.predict(X_val)
            score = self._calculate_metric(y_val, pred)
            scores.append(score)

        return np.mean(scores)

    def _calculate_metric(self, y_true: np.ndarray,
                          y_pred: np.ndarray) -> float:
        """Calcule la métrique d'optimisation"""
        if self.config.optimization_metric == 'sharpe_ratio':
            returns = pd.Series(y_pred) / pd.Series(y_true) - 1
            return returns.mean() / returns.std() * np.sqrt(252)
        elif self.config.optimization_metric == 'rmse':
            return -np.sqrt(np.mean((y_true - y_pred) ** 2))
        else:
            raise ValueError(f"Métrique non supportée: {self.config.optimization_metric}")


class EnsembleModel:
    def __init__(self,
                 base_models: List[Dict[str, Any]],
                 ensemble_method: str = 'weighted'):
        self.base_models = base_models
        self.ensemble_method = ensemble_method
        self.trained_models = []
        self.weights = None

    def train(self, X: np.ndarray, y: np.ndarray):
        """Entraîne l'ensemble de modèles"""
        predictions = np.zeros((len(self.base_models), len(y)))

        # Entraînement des modèles de base
        for i, model_config in enumerate(self.base_models):
            model = self._create_model(model_config)
            model.fit(X, y)
            self.trained_models.append(model)
            predictions[i] = model.predict(X)

        # Calcul des poids de l'ensemble
        if self.ensemble_method == 'weighted':
            self.weights = self._calculate_optimal_weights(predictions, y)
        else:
            self.weights = np.ones(len(self.base_models)) / len(self.base_models)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Fait des prédictions avec l'ensemble"""
        predictions = np.zeros((len(self.trained_models), len(X)))

        for i, model in enumerate(self.trained_models):
            predictions[i] = model.predict(X)

        return np.average(predictions, axis=0, weights=self.weights)

    def _create_model(self, config: Dict) -> Any:
        """Crée un modèle selon la configuration"""
        model_type = config['type']
        params = config['params']

        if model_type == 'lightgbm':
            return lgb.LGBMRegressor(**params)
        elif model_type == 'xgboost':
            return xgb.XGBRegressor(**params)
        elif model_type == 'lstm':
            return self._create_lstm_model(params)
        else:
            raise ValueError(f"Type de modèle non supporté: {model_type}")

    def _calculate_optimal_weights(self,
                                   predictions: np.ndarray,
                                   y_true: np.ndarray) -> np.ndarray:
        """Calcule les poids optimaux pour l'ensemble"""

        # Optimisation des poids par minimisation de l'erreur
        def objective(weights):
            weighted_pred = np.average(predictions, axis=0, weights=weights)
            return np.sqrt(np.mean((y_true - weighted_pred) ** 2))

        # Contraintes: somme des poids = 1, poids >= 0
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        )
        bounds = [(0, 1) for _ in range(len(self.base_models))]

        # Optimisation
        from scipy.optimize import minimize
        result = minimize(
            objective,
            x0=np.ones(len(self.base_models)) / len(self.base_models),
            method='SLSQP',
            constraints=constraints,
            bounds=bounds
        )

        return result.x


class ModelEvaluator:
    def __init__(self):
        self.metrics = {}

    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Évalue les performances du modèle"""
        self.metrics = {
            'rmse': np.sqrt(np.mean((y_true - y_pred) ** 2)),
            'mae': np.mean(np.abs(y_true - y_pred)),
            'r2': 1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        }

        # Métriques de trading
        returns = pd.Series(y_pred) / pd.Series(y_true) - 1
        self.metrics.update({
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252),
            'max_drawdown': self._calculate_max_drawdown(returns),
            'win_rate': np.mean(returns > 0) * 100
        })

        return self.metrics

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calcule le maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return float(drawdown.min())

