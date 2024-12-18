
from rest_framework import serializers
from ..models import TradingStrategy, Trade, Position
from ..models.exchange_key import ExchangeKey


class TradingStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingStrategy
        fields = '__all__'

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'

class PositionSerializer(serializers.ModelSerializer):
    pnl = serializers.SerializerMethodField()
    current_value = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = '__all__'

    def get_pnl(self, obj):
        return obj.calculate_pnl()

    def get_current_value(self, obj):
        return obj.current_value


class ExchangeKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeKey
        fields = ['id', 'exchange', 'api_key', 'api_secret', 'testnet', 'is_active', 'last_checked']
        extra_kwargs = {
            'api_secret': {'write_only': True},
            'api_key': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)