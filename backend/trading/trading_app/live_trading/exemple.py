import asyncio
import time

from .executor import LiveTradingSystem

if __name__ == "__main__":
    # Configuration du système
    config = {
        'api_key': 'your_api_key',
        'api_secret': 'your_api_secret',
        'symbols': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
        'min_confidence': 0.7,
        'position_size': 0.02,  # 2% du capital
        'max_position_size': 0.1,  # 10% du capital
        'max_exposure': 0.5,  # 50% du capital
        'trailing_stop_pct': 0.02,  # 2%
        'risk_free_rate': 0.02,
        'max_drawdown': 0.15  # 15%
    }

    # Création et démarrage du système
    trading_system = LiveTradingSystem(config)

    try:
        # Démarrage du système
        asyncio.run(trading_system.start())

        # Boucle principale
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Arrêt propre du système
        asyncio.run(trading_system.stop())
        print("Système arrêté proprement")