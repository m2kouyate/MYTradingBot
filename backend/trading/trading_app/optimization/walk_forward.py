from typing import List, Dict

from .parameter_optimizer import StrategyOptimizer


class WalkForwardOptimizer:
    def __init__(self,
                 strategy_optimizer: StrategyOptimizer,
                 window_size: int = 60,
                 step_size: int = 20):
        self.strategy_optimizer = strategy_optimizer
        self.window_size = window_size
        self.step_size = step_size

    def optimize(self, data: pd.DataFrame) -> List[Dict]:
        """Effectue une optimisation walk-forward"""
        results = []
        total_periods = len(data)

        for start_idx in range(0, total_periods - self.window_size, self.step_size):
            end_idx = start_idx + self.window_size
            in_sample_data = data.iloc[start_idx:end_idx]

            # Optimisation sur la période in-sample
            self.strategy_optimizer.data = in_sample_data
            optimization_result = self.strategy_optimizer.optimize()

            # Test sur la période out-of-sample
            if end_idx + self.step_size <= total_periods:
                out_sample_data = data.iloc[end_idx:end_idx + self.step_size]
                out_sample_metrics = self.strategy_optimizer._calculate_metrics(
                    optimization_result.parameters,
                    out_sample_data
                )

                results.append({
                    'period': (start_idx, end_idx),
                    'parameters': optimization_result.parameters,
                    'in_sample_metrics': optimization_result.performance_metrics,
                    'out_sample_metrics': out_sample_metrics,
                    'robustness': optimization_result.robustness_score
                })

        return results