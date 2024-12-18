
from django.contrib.auth.models import User
from django.db import models


class TradingStrategy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    # Paramètres de la stratégie
    buy_threshold = models.DecimalField(max_digits=10, decimal_places=2)
    sell_threshold = models.DecimalField(max_digits=10, decimal_places=2)
    stop_loss = models.DecimalField(max_digits=10, decimal_places=2)
    take_profit = models.DecimalField(max_digits=10, decimal_places=2)
