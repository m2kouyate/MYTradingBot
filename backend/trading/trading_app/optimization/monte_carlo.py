
from typing import Dict, List, Tuple, Callable
import numpy as np
import pandas as pd


class MonteCarloSimulator:
    def __init__(self,
                 strategy,
                 data: pd.DataFrame,
                 num_simulations: int = 1000):
        self.strategy = strategy
        self.data = data
        self.num_simulations = num_simulations

    def simulate(self) -> Dict:
        """Effectue des simulations Monte Carlo"""
        simulation_results = []

        for _ in range(self.num_simulations):
            # Simulation avec bruit sur les prix
            noisy_data = self._add_noise_to_data()
            backtest_result = self.strategy._run_backtest(noisy_data)
            simulation_results.append(self._calculate_metrics(backtest_result))

        return self._analyze_simulation_results(simulation_results)

    def _add_noise_to_data(self) -> pd.DataFrame:
        """Ajoute du bruit gaussien aux données"""
        noisy_data = self.data.copy()
        noise = np.random.normal(0, 0.001, len(self.data))
        noisy_data['close'] = noisy_data['close'] * (1 + noise)
        return noisy_data

    def _analyze_simulation_results(self,
                                    results: List[Dict]) -> Dict:
        """Analyse les résultats des simulations"""
        metrics = {}
        for metric in results[0].keys():
            values = [result[metric] for result in results]
            metrics[metric] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'percentile_5': np.percentile(values, 5),
                'percentile_95': np.percentile(values, 95)
            }

        return metrics