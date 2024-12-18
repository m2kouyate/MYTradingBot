from ..example import EnhancedTradingStrategy
from .monte_carlo import MonteCarloSimulator
from .parameter_optimizer import StrategyOptimizer
from .walk_forward import WalkForwardOptimizer

if __name__ == "__main__":
    # Configuration des paramètres à optimiser
    param_ranges = {
        'rsi_period': (10, 30),
        'rsi_oversold': (20, 40),
        'rsi_overbought': (60, 80),
        'macd_fast': (8, 20),
        'macd_slow': (20, 40),
        'macd_signal': (5, 15)
    }

    # Création de l'optimiseur
    optimizer = StrategyOptimizer(
        strategy_class=EnhancedTradingStrategy,
        parameter_ranges=param_ranges,
        data=historical_data,
        initial_capital=10000.0
    )

    # Optimisation des paramètres
    optimization_result = optimizer.optimize(
        metric='sharpe_ratio',
        method='differential_evolution'
    )

    # Walk-forward optimization
    wf_optimizer = WalkForwardOptimizer(optimizer)
    wf_results = wf_optimizer.optimize(historical_data)

    # Monte Carlo simulation
    mc_simulator = MonteCarloSimulator(
        strategy=EnhancedTradingStrategy(optimization_result.parameters),
        data=historical_data
    )
    mc_results = mc_simulator.simulate()

    # Affichage des résultats
    print("Paramètres optimaux:", optimization_result.parameters)
    print("Métriques de performance:", optimization_result.performance_metrics)
    print("Score de robustesse:", optimization_result.robustness_score)