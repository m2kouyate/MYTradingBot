import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .services import MarketDataService, PortfolioService


class TradingDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            'trading_dashboard',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'trading_dashboard',
            self.channel_name
        )

    async def receive(self, text_data):
        """Gère les messages reçus du client"""
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'subscribe_market_data':
            await self.handle_market_data_subscription(data)
        elif message_type == 'subscribe_portfolio':
            await self.handle_portfolio_subscription(data)

    async def send_update(self, event):
        """Envoie les mises à jour au client"""
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'data': event['data']
        }))

    async def handle_market_data_subscription(self, data):
        """Gère les souscriptions aux données de marché"""
        symbols = data.get('symbols', [])
        service = MarketDataService()

        for symbol in symbols:
            await service.subscribe(symbol, self.channel_name)

    async def handle_portfolio_subscription(self, data):
        """Gère les souscriptions aux données du portfolio"""
        service = PortfolioService()
        await service.subscribe(self.channel_name)
