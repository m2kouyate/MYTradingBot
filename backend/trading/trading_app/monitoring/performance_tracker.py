
from decimal import Decimal
from typing import Dict
import numpy as np


class PerformanceTracker:
    def __init__(self):
        self.trades_history = []
        self.daily_stats = {}

    def add_trade(self, trade: Dict):
        """Ajoute un trade à l'historique et met à jour les statistiques"""
        self.trades_history.append(trade)
        self._update_daily_stats(trade)

    def get_performance_metrics(self) -> Dict:
        """Calcule les métriques de performance"""
        if not self.trades_history:
            return {}

        total_trades = len(self.trades_history)
        winning_trades = len([t for t in self.trades_history if t['profit'] > 0])

        return {
            'total_trades': total_trades,
            'win_rate': winning_trades / total_trades,
            'average_profit': sum(t['profit'] for t in self.trades_history) / total_trades,
            'max_drawdown': self._calculate_max_drawdown(),
            'sharpe_ratio': self._calculate_sharpe_ratio(),
            'profit_factor': self._calculate_profit_factor()
        }

    def _calculate_max_drawdown(self) -> Decimal:
        """Calcule le drawdown maximum"""
        equity_curve = self._generate_equity_curve()
        running_max = float('-inf')
        max_drawdown = 0

        for value in equity_curve:
            running_max = max(running_max, value)
            drawdown = (running_max - value) / running_max
            max_drawdown = max(max_drawdown, drawdown)

        return Decimal(str(max_drawdown))

    def _calculate_sharpe_ratio(self) -> float:
        """Calcule le ratio de Sharpe"""
        returns = self._calculate_daily_returns()
        if not returns:
            return 0

        return (np.mean(returns) / np.std(returns)) * np.sqrt(252)

    def _calculate_profit_factor(self) -> Decimal:
        """Calcule le facteur de profit"""
        gross_profit = sum(t['profit'] for t in self.trades_history if t['profit'] > 0)
        gross_loss = abs(sum(t['profit'] for t in self.trades_history if t['profit'] < 0))

        return gross_profit / gross_loss if gross_loss != 0 else Decimal('0')