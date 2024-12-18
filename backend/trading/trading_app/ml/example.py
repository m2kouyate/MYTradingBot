from .ensemble_trading import EnsembleTradingSystem
from .optimization import EnsembleModel, HyperparameterOptimizer, OptimizationConfig

if __name__ == "__main__":
    # Chargement et préparation des données
    market_data = pd.read_csv('market_data.csv', parse_dates=['timestamp'])
    market_data.set_index('timestamp', inplace=True)

    # Configuration et optimisation des modèles
    config = OptimizationConfig(
        n_trials=100,
        cv_folds=5,
        optimization_metric='sharpe_ratio'
    )

    # Optimisation des hyperparamètres pour chaque type de modèle
    optimizers = {
        'lightgbm': HyperparameterOptimizer('lightgbm', config),
        'xgboost': HyperparameterOptimizer('xgboost', config),
        'lstm': HyperparameterOptimizer('lstm', config)
    }

    best_params = {}
    for model_type, optimizer in optimizers.items():
        best_params[model_type] = optimizer.optimize(X_train, y_train)

    # Création de l'ensemble
    base_models = [
        {'type': 'lightgbm', 'params': best_params['lightgbm']},
        {'type': 'xgboost', 'params': best_params['xgboost']},
        {'type': 'lstm', 'params': best_params['lstm']}
    ]

    ensemble = EnsembleModel(base_models, ensemble_method='weighted')
    ensemble.train(X_train, y_train)

    # Création du système de trading
    trading_system = EnsembleTradingSystem(
        ensemble_model=ensemble,
        confidence_threshold=0.7,
        min_model_agreement=0.6
    )

    # Génération des signaux
    signals = trading_system.generate_signals(market_data)

    # Évaluation des performances
    performance = trading_system.evaluate_performance(market_data)

    # Affichage des résultats
    print("Performance du système de trading:")
    for metric, value in performance.items():
        print(f"{metric}: {value}")

    # Sauvegarde du modèle
    trading_system.save_model('ensemble_trading_system.joblib')