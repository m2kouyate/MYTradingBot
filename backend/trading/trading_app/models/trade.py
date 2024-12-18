
from django.db import models
from .trading_strategy import TradingStrategy

class Trade(models.Model):
    strategy = models.ForeignKey(TradingStrategy, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    entry_price = models.DecimalField(max_digits=20, decimal_places=8)
    exit_price = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True)
    profit_loss = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    status = models.CharField(max_length=20, choices=[
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled')
    ])