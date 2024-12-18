from typing import Dict, List, Tuple, Callable
import numpy as np
from scipy.optimize import differential_evolution
import pandas as pd
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
import itertools


@dataclass
class OptimizationResult:
    parameters: Dict[str, float]
    performance_metrics: Dict[str, float]
    robustness_score: float
    validation_metrics: Dict[str, float]
    optimization_path: List[Dict]


class StrategyOptimizer:
    def __init__(self,
                 strategy_class,
                 parameter_ranges: Dict[str, Tuple[float, float]],
                 data: pd.DataFrame,
                 initial_capital: float = 10000.0):
        self.strategy_class = strategy_class
        self.parameter_ranges = parameter_ranges
        self.data = data
        self.initial_capital = initial_capital
        self.optimization_history = []

    def optimize(self,
                 metric: str = 'sharpe_ratio',
                 method: str = 'differential_evolution',
                 max_iterations: int = 100,
                 population_size: int = 15) -> OptimizationResult:
        """Optimise les paramètres de la stratégie"""

        # Préparation des données
        train_data, val_data = self._split_data_train_val()

        # Configuration de l'optimisation
        bounds = [param_range for param_range in self.parameter_ranges.values()]
        param_names = list(self.parameter_ranges.keys())

        if method == 'differential_evolution':
            result = differential_evolution(
                func=lambda x: -self._evaluate_parameters(
                    dict(zip(param_names, x)),
                    train_data,
                    metric
                ),
                bounds=bounds,
                maxiter=max_iterations,
                popsize=population_size,
                mutation=(0.5, 1.0),
                recombination=0.7,
                workers=-1
            )

            optimal_params = dict(zip(param_names, result.x))

        elif method == 'grid_search':
            optimal_params = self._grid_search(
                train_data,
                metric,
                max_iterations
            )

        # Validation des résultats
        train_metrics = self._calculate_metrics(optimal_params, train_data)
        val_metrics = self._calculate_metrics(optimal_params, val_data)
        robustness = self._calculate_robustness_score(
            optimal_params,
            train_metrics,
            val_metrics
        )

        return OptimizationResult(
            parameters=optimal_params,
            performance_metrics=train_metrics,
            robustness_score=robustness,
            validation_metrics=val_metrics,
            optimization_path=self.optimization_history
        )

    def _grid_search(self,
                     data: pd.DataFrame,
                     metric: str,
                     max_iterations: int) -> Dict[str, float]:
        """Effectue une recherche par grille des paramètres optimaux"""
        param_combinations = self._generate_parameter_grid(max_iterations)

        with ProcessPoolExecutor() as executor:
            results = list(executor.map(
                lambda params: (
                    params,
                    self._evaluate_parameters(params, data, metric)
                ),
                param_combinations
            ))

        best_params, _ = max(results, key=lambda x: x[1])
        return best_params

    def _generate_parameter_grid(self, max_points: int) -> List[Dict]:
        """Génère une grille de paramètres à tester"""
        points_per_dim = int(np.power(max_points, 1 / len(self.parameter_ranges)))

        grid_points = {}
        for param, (min_val, max_val) in self.parameter_ranges.items():
            grid_points[param] = np.linspace(min_val, max_val, points_per_dim)

        combinations = itertools.product(*grid_points.values())
        return [dict(zip(grid_points.keys(), combo)) for combo in combinations]

    def _evaluate_parameters(self,
                             parameters: Dict[str, float],
                             data: pd.DataFrame,
                             metric: str) -> float:
        """Évalue un ensemble de paramètres"""
        strategy = self.strategy_class(parameters)
        backtest_result = self._run_backtest(strategy, data)
        metrics = self._calculate_metrics(parameters, data)

        self.optimization_history.append({
            'parameters': parameters,
            'metrics': metrics
        })

        return metrics[metric]

    def _calculate_metrics(self,
                           parameters: Dict[str, float],
                           data: pd.DataFrame) -> Dict[str, float]:
        """Calcule les métriques de performance"""
        strategy = self.strategy_class(parameters)
        backtest_result = self._run_backtest(strategy, data)

        returns = self._calculate_returns(backtest_result)

        return {
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'max_drawdown': self._calculate_max_drawdown(returns),
            'total_return': self._calculate_total_return(returns),
            'win_rate': self._calculate_win_rate(backtest_result),
            'profit_factor': self._calculate_profit_factor(backtest_result),
            'sortino_ratio': self._calculate_sortino_ratio(returns),
            'calmar_ratio': self._calculate_calmar_ratio(returns)
        }

    def _calculate_robustness_score(self,
                                    parameters: Dict[str, float],
                                    train_metrics: Dict[str, float],
                                    val_metrics: Dict[str, float]) -> float:
        """Calcule un score de robustesse"""
        # Comparaison des performances entre training et validation
        metric_differences = []
        for metric in train_metrics:
            if metric in val_metrics:
                diff = abs(train_metrics[metric] - val_metrics[metric])
                rel_diff = diff / abs(train_metrics[metric]) if train_metrics[metric] != 0 else float('inf')
                metric_differences.append(rel_diff)

        # Plus le score est proche de 1, plus la stratégie est robuste
        return 1 / (1 + np.mean(metric_differences))
