import pandas as pd
from django.conf import settings

from backend.trading.trading_app.live_trading.executor import LiveTradingSystem
from .models import TradingStrategy


def test_strategy():
    # Chargez des données historiques
    data = pd.read_csv('data/market_data.csv')

    # Créez une instance de stratégie
    strategy = TradingStrategy(settings.TRADING_CONFIG)

    # Testez le backtesting
    results = strategy.backtest(data)
    print("Résultats du backtest :")
    print(f"Rendement total : {results['total_return']}%")
    print(f"Ratio Sharpe : {results['sharpe_ratio']}")

    return results


def test_live_system():
    # Créez une instance du système en mode test
    system = LiveTradingSystem(
        config={**settings.TRADING_CONFIG, 'test_mode': True}
    )

    # Testez la connexion à Binance
    if system.test_connection():
        print("Connexion à Binance réussie")
    else:
        print("Erreur de connexion à Binance")

    return system


if __name__ == "__main__":
    print("Démarrage des tests...")
    test_results = test_strategy()
    test_system = test_live_system()