
from datetime import datetime
from decimal import Decimal
from binance.client import Client
from typing import Dict, List, Type
import pandas as pd
import numpy as np
from .data_feed import HistoricalDataFeed
from ..strategies.base_strategy import BaseStrategy


class BacktestResult:
    def __init__(self):
        self.trades: List[Dict] = []
        self.equity_curve: pd.Series = None
        self.metrics: Dict = {}

    def calculate_metrics(self):
        """Calcule les métriques de performance du backtest"""
        if not self.trades:
            return

        # Métriques de base
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t['pnl'] > 0])

        self.metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_pnl': sum(t['pnl'] for t in self.trades),
            'avg_pnl': sum(t['pnl'] for t in self.trades) / total_trades if total_trades > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(),
            'sharpe_ratio': self._calculate_sharpe_ratio(),
            'sortino_ratio': self._calculate_sortino_ratio(),
            'risk_adjusted_return': self._calculate_risk_adjusted_return()
        }

    def _calculate_max_drawdown(self) -> float:
        """Calcule le drawdown maximum"""
        if self.equity_curve is None:
            return 0

        rolling_max = self.equity_curve.expanding().max()
        drawdowns = (self.equity_curve - rolling_max) / rolling_max
        return float(drawdowns.min())

    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calcule le ratio de Sharpe"""
        if self.equity_curve is None:
            return 0

        returns = self.equity_curve.pct_change().dropna()
        excess_returns = returns - risk_free_rate / 252

        if len(returns) < 2:
            return 0

        return float(excess_returns.mean() / returns.std() * np.sqrt(252))

    def _calculate_sortino_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calcule le ratio de Sortino"""
        if self.equity_curve is None:
            return 0

        returns = self.equity_curve.pct_change().dropna()
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]

        if len(downside_returns) < 2:
            return 0

        return float(excess_returns.mean() / downside_returns.std() * np.sqrt(252))


class BacktestEngine:
    def __init__(
            self,
            data_feed: HistoricalDataFeed,
            initial_capital: float = 10000.0,
            commission: float = 0.001
    ):
        self.data_feed = data_feed
        self.initial_capital = initial_capital
        self.commission = commission
        self.current_capital = initial_capital
        self.position = None
        self.result = BacktestResult()

    def run(
            self,
            strategy: BaseStrategy,
            symbol: str,
            start_time: datetime,
            end_time: datetime,
            interval: str = Client.KLINE_INTERVAL_1HOUR
    ) -> BacktestResult:
        """
        Exécute le backtest d'une stratégie
        """
        # Récupération des données historiques
        data = self.data_feed.get_historical_data(
            symbol, start_time, end_time, interval
        )

        equity_history = []

        # Simulation trade par trade
        for timestamp, row in data.iterrows():
            current_price = float(row['close'])

            # Mise à jour de la valeur du portfolio
            equity_history.append(self._calculate_equity(current_price))

            # Vérification des signaux de trading
            if self.position is None:
                if strategy.should_buy(symbol, Decimal(str(current_price))):
                    self._enter_position(timestamp, current_price, symbol)
            else:
                if strategy.should_sell(
                        symbol,
                        Decimal(str(current_price)),
                        Decimal(str(self.position['entry_price']))
                ):
                    self._exit_position(timestamp, current_price)

        # Création de la courbe d'équité
        self.result.equity_curve = pd.Series(
            equity_history,
            index=data.index,
            name='equity'
        )

        # Calcul des métriques finales
        self.result.calculate_metrics()

        return self.result

    def _enter_position(self, timestamp: datetime, price: float, symbol: str, allocation: float = 0.95):
        """Ouvre une nouvelle position"""
        position_size = self.current_capital * allocation  # 95% du capital
        quantity = position_size / price
        commission_cost = position_size * self.commission

        self.position = {
            'entry_time': timestamp,
            'entry_price': price,
            'quantity': quantity,
            'symbol': symbol,
            'commission': commission_cost
        }

        self.current_capital -= commission_cost

    def _exit_position(self, timestamp: datetime, price: float):
        """Ferme la position existante"""
        if self.position is None:
            return

        exit_value = self.position['quantity'] * price
        commission_cost = exit_value * self.commission

        pnl = (
                exit_value -
                (self.position['quantity'] * self.position['entry_price']) -
                self.position['commission'] -
                commission_cost
        )

        self.current_capital = exit_value - commission_cost

        trade_record = {
            'entry_time': self.position['entry_time'],
            'exit_time': timestamp,
            'symbol': self.position['symbol'],
            'entry_price': self.position['entry_price'],
            'exit_price': price,
            'quantity': self.position['quantity'],
            'pnl': pnl,
            'return': pnl / (self.position['quantity'] * self.position['entry_price'])
        }

        self.result.trades.append(trade_record)
        self.position = None

    def _calculate_equity(self, current_price: float) -> float:
        """Calcule la valeur actuelle du portfolio"""
        if self.position is None:
            return self.current_capital

        position_value = self.position['quantity'] * current_price
        return position_value + self.current_capital
