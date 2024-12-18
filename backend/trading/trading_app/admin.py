from django.contrib import admin
from .models import TradingStrategy, Trade, Position

admin.site.register(TradingStrategy)
admin.site.register(Trade)
admin.site.register(Position)