
from django.db import models
from .trade import Trade
from .trading_strategy import TradingStrategy


class Position(models.Model):
    strategy = models.ForeignKey(TradingStrategy, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    entry_price = models.DecimalField(max_digits=20, decimal_places=8)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    entry_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed')
    ])
    current_price = models.DecimalField(max_digits=20, decimal_places=8, null=True)

    def calculate_pnl(self):
        if self.current_price:
            return (self.current_price - self.entry_price) * self.quantity
        return 0

    @property
    def current_value(self):
        return self.quantity * self.current_price if self.current_price else 0