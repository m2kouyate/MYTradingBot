from typing import Dict, List, Optional
import asyncio
import websockets
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.websockets import BinanceSocketManager
from dataclasses import dataclass
import logging
import redis
import queue
from threading import Thread


@dataclass
class TradeExecution:
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: float
    price: float
    type: str  # 'MARKET' or 'LIMIT'
    time_in_force: str = 'GTC'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


class LiveTradingSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.client = Client(
            config['api_key'],
            config['api_secret']
        )
        self.bsm = BinanceSocketManager(self.client)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.order_queue = queue.Queue()
        self.active_trades = {}
        self.running = False

    async def start(self):
        """Démarre le système de trading en temps réel"""
        self.running = True

        # Démarrage des workers
        asyncio.create_task(self._process_market_data())
        asyncio.create_task(self._process_orders())
        asyncio.create_task(self._monitor_positions())
        asyncio.create_task(self._risk_manager())

        # Connexion aux websockets
        conn_key = self.bsm.start_multiplex_socket(
            self.config['symbols'],
            self._handle_socket_message
        )
        self.bsm.start()

        logging.info("Système de trading en temps réel démarré")

    async def stop(self):
        """Arrête le système de trading"""
        self.running = False
        self.bsm.stop_socket(self.conn_key)
        self.bsm.close()

        # Fermeture des positions ouvertes
        await self._close_all_positions()
        logging.info("Système de trading arrêté")

    async def _process_market_data(self):
        """Traite les données de marché en temps réel"""
        while self.running:
            try:
                # Récupération des dernières données
                for symbol in self.config['symbols']:
                    market_data = self._get_market_data(symbol)

                    # Mise à jour des indicateurs
                    indicators = self._update_indicators(market_data)

                    # Génération des signaux
                    signals = await self._generate_signals(
                        symbol,
                        market_data,
                        indicators
                    )

                    # Traitement des signaux
                    if signals:
                        await self._handle_trading_signals(signals)

                await asyncio.sleep(1)  # Intervalle de mise à jour

            except Exception as e:
                logging.error(f"Erreur dans le traitement des données: {str(e)}")

    async def _process_orders(self):
        """Traite la file d'attente des ordres"""
        while self.running:
            try:
                while not self.order_queue.empty():
                    order = self.order_queue.get()
                    await self._execute_order(order)

                await asyncio.sleep(0.1)

            except Exception as e:
                logging.error(f"Erreur dans le traitement des ordres: {str(e)}")

    async def _execute_order(self, trade_execution: TradeExecution):
        """Exécute un ordre sur le marché"""
        try:
            # Vérification du capital disponible
            if not self._check_capital_available(trade_execution):
                logging.warning("Capital insuffisant pour l'exécution")
                return

            # Placement de l'ordre principal
            order = self.client.create_order(
                symbol=trade_execution.symbol,
                side=trade_execution.side,
                type=trade_execution.type,
                quantity=trade_execution.quantity,
                price=trade_execution.price if trade_execution.type == 'LIMIT' else None,
                timeInForce=trade_execution.time_in_force if trade_execution.type == 'LIMIT' else None
            )

            # Placement des ordres stop loss et take profit
            if order['status'] == 'FILLED':
                if trade_execution.stop_loss:
                    self._place_stop_loss(trade_execution)
                if trade_execution.take_profit:
                    self._place_take_profit(trade_execution)

            # Mise à jour des positions actives
            self._update_active_trades(order, trade_execution)

            # Notification de l'exécution
            await self._notify_execution(order)

        except BinanceAPIException as e:
            logging.error(f"Erreur Binance lors de l'exécution: {str(e)}")
        except Exception as e:
            logging.error(f"Erreur lors de l'exécution: {str(e)}")

    async def _monitor_positions(self):
        """Surveille les positions ouvertes"""
        while self.running:
            try:
                for symbol, trade in self.active_trades.items():
                    current_price = float(
                        self.client.get_symbol_ticker(symbol=symbol)['price']
                    )

                    # Vérification des niveaux de stop loss et take profit
                    if self._check_stop_loss(trade, current_price):
                        await self._close_position(symbol, 'stop_loss')
                    elif self._check_take_profit(trade, current_price):
                        await self._close_position(symbol, 'take_profit')

                    # Mise à jour des trailing stops
                    await self._update_trailing_stops(trade, current_price)

                await asyncio.sleep(1)

            except Exception as e:
                logging.error(f"Erreur dans la surveillance: {str(e)}")

    async def _risk_manager(self):
        """Gère les risques en temps réel"""
        while self.running:
            try:
                # Calcul de l'exposition totale
                total_exposure = self._calculate_total_exposure()

                # Vérification des limites de risque
                if total_exposure > self.config['max_exposure']:
                    await self._reduce_exposure()

                # Vérification de la diversification
                await self._check_diversification()

                # Vérification des pertes maximales
                if self._check_max_drawdown():
                    await self._hedge_positions()

                await asyncio.sleep(5)

            except Exception as e:
                logging.error(f"Erreur dans la gestion des risques: {str(e)}")

    async def _handle_trading_signals(self, signals: Dict):
        """Traite les signaux de trading"""
        for signal in signals:
            if self._validate_signal(signal):
                # Calcul de la taille de la position
                position_size = self._calculate_position_size(signal)

                # Création de l'ordre
                trade_execution = TradeExecution(
                    symbol=signal['symbol'],
                    side='BUY' if signal['direction'] == 'buy' else 'SELL',
                    quantity=position_size,
                    price=signal.get('price'),
                    type='MARKET',
                    stop_loss=signal.get('stop_loss'),
                    take_profit=signal.get('take_profit')
                )

                # Ajout à la file d'attente
                self.order_queue.put(trade_execution)

    def _validate_signal(self, signal: Dict) -> bool:
        """Valide un signal de trading"""
        # Vérification de la confiance du signal
        if signal.get('confidence', 0) < self.config['min_confidence']:
            return False

        # Vérification des conditions de marché
        if not self._check_market_conditions(signal['symbol']):
            return False

        # Vérification des filtres de trading
        if not self._check_trading_filters(signal):
            return False

        return True

    def _calculate_position_size(self, signal: Dict) -> float:
        """Calcule la taille de la position"""
        account_balance = float(
            self.client.get_asset_balance(
                asset='USDT'
            )['free']
        )

        # Position de base (% du capital)
        base_size = account_balance * self.config['position_size']

        # Ajustement selon la confiance du signal
        adjusted_size = base_size * signal.get('confidence', 1)

        # Ajustement selon la volatilité
        volatility_factor = self._calculate_volatility_factor(signal['symbol'])
        final_size = adjusted_size * volatility_factor

        # Application des limites
        return min(
            final_size,
            self.config['max_position_size']
        )

    def _update_trailing_stops(self, trade: Dict, current_price: float):
        """Met à jour les trailing stops"""
        if trade.get('trailing_stop'):
            if trade['side'] == 'BUY':
                new_stop = current_price * (1 - self.config['trailing_stop_pct'])
                if new_stop > trade['stop_loss']:
                    trade['stop_loss'] = new_stop
            else:
                new_stop = current_price * (1 + self.config['trailing_stop_pct'])
                if new_stop < trade['stop_loss']:
                    trade['stop_loss'] = new_stop

    async def _close_position(self, symbol: str, reason: str):
        """Ferme une position"""
        trade = self.active_trades[symbol]

        try:
            # Création de l'ordre de fermeture
            close_order = self.client.create_order(
                symbol=symbol,
                side='SELL' if trade['side'] == 'BUY' else 'BUY',
                type='MARKET',
                quantity=trade['quantity']
            )

            # Calcul du P&L
            pnl = self._calculate_pnl(trade, close_order)

            # Mise à jour des statistiques
            self._update_trading_stats(trade, pnl, reason)

            # Suppression de la position active
            del self.active_trades[symbol]

            # Notification
            await self._notify_position_closed(trade, pnl, reason)

        except Exception as e:
            logging.error(f"Erreur lors de la fermeture: {str(e)}")

    def _calculate_pnl(self, trade: Dict, close_order: Dict) -> float:
        """Calcule le P&L d'une position"""
        entry_value = float(trade['quantity']) * float(trade['entry_price'])
        exit_value = float(trade['quantity']) * float(close_order['price'])

        if trade['side'] == 'BUY':
            return exit_value - entry_value
        else:
            return entry_value - exit_value
