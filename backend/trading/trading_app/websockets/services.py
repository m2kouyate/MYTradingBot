import asyncio
from datetime import datetime
from typing import Dict, List
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from ..models import Position, Trade, TradingStrategy


class MarketDataService:
    def __init__(self):
        self.subscriptions: Dict[str, List[str]] = {}
        self.running = False

    async def subscribe(self, symbol: str, channel_name: str):
        """Ajoute une souscription pour un symbole"""
        if symbol not in self.subscriptions:
            self.subscriptions[symbol] = []
        self.subscriptions[symbol].append(channel_name)

        if not self.running:
            self.running = True
            asyncio.create_task(self.start_market_data_stream())

    async def unsubscribe(self, symbol: str, channel_name: str):
        """Retire une souscription"""
        if symbol in self.subscriptions:
            self.subscriptions[symbol].remove(channel_name)

    async def start_market_data_stream(self):
        """Démarre le flux de données de marché"""
        channel_layer = get_channel_layer()

        while self.running:
            for symbol in self.subscriptions:
                market_data = await self.get_market_data(symbol)

                for channel_name in self.subscriptions[symbol]:
                    await channel_layer.send(channel_name, {
                        'type': 'send_update',
                        'data': {
                            'type': 'market_data',
                            'symbol': symbol,
                            'data': market_data
                        }
                    })

            await asyncio.sleep(1)  # Intervalle de mise à jour

    @sync_to_async
    def get_market_data(self, symbol: str) -> Dict:
        """Récupère les données de marché pour un symbole"""
        # Implémentation de la récupération des données
        pass


class PortfolioService:
    def __init__(self):
        self.subscriptions: List[str] = []
        self.running = False

    async def subscribe(self, channel_name: str):
        """Ajoute une souscription au portfolio"""
        self.subscriptions.append(channel_name)

        if not self.running:
            self.running = True
            asyncio.create_task(self.start_portfolio_updates())

    async def unsubscribe(self, channel_name: str):
        """Retire une souscription"""
        self.subscriptions.remove(channel_name)

    async def start_portfolio_updates(self):
        """Démarre les mises à jour du portfolio"""
        channel_layer = get_channel_layer()

        while self.running:
            portfolio_data = await self.get_portfolio_data()

            for channel_name in self.subscriptions:
                await channel_layer.send(channel_name, {
                    'type': 'send_update',
                    'data': {
                        'type': 'portfolio_update',
                        'data': portfolio_data
                    }
                })

            await asyncio.sleep(5)  # Intervalle de mise à jour

    @sync_to_async
    def get_portfolio_data(self) -> Dict:
        """Récupère les données du portfolio"""
        positions = Position.objects.filter(status='OPEN')
        return {
            'positions': [{
                'symbol': pos.symbol,
                'quantity': pos.quantity,
                'entry_price': pos.entry_price,
                'current_price': pos.current_price,
                'pnl': pos.calculate_pnl()
            } for pos in positions],
            'total_value': sum(pos.current_value for pos in positions),
            'day_pnl': self.calculate_day_pnl()
        }

    def calculate_day_pnl(self) -> float:
        """Calcule le P&L de la journée"""
        today_trades = Trade.objects.filter(
            exit_time__date=datetime.now().date()
        )
        return sum(trade.profit_loss for trade in today_trades)
