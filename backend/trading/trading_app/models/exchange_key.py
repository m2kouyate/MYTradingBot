# models/exchange_key.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class ExchangeKey(models.Model):
    EXCHANGE_CHOICES = [
        ('BINANCE', 'Binance'),
        ('BYBIT', 'Bybit'),  # На будущее
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.CharField(max_length=20, choices=EXCHANGE_CHOICES)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)
    testnet = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_checked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'exchange'], name='unique_user_exchange')
        ]

    def __str__(self):
        return f"{self.user.username} - {self.exchange}"

    def update_last_checked(self):
        """Обновляет поле last_checked."""
        self.last_checked = timezone.now()
        self.save(update_fields=['last_checked'])

    def save(self, *args, **kwargs):
        """
        Переопределение метода save().
        Проверяет дату last_checked перед сохранением.
        """
        if not self.last_checked or timezone.now() - self.last_checked > timezone.timedelta(days=1):
            self.last_checked = timezone.now()
        super().save(*args, **kwargs)
