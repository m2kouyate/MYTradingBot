

from typing import Dict


class NotificationService:
    def __init__(self, config: Dict):
        self.email_config = config.get('email', {})
        self.telegram_config = config.get('telegram', {})

    def send_trade_notification(self, trade: Dict):
        """Envoie une notification pour un nouveau trade"""
        message = self._format_trade_message(trade)
        self._send_email(message)
        self._send_telegram(message)

    def send_alert(self, alert_type: str, message: str):
        """Envoie une alerte (stop-loss, take-profit, etc.)"""
        formatted_message = f"ALERT [{alert_type}]: {message}"
        self._send_email(formatted_message)
        self._send_telegram(formatted_message)

    def _send_email(self, message: str):
        # Implémentation de l'envoi d'email
        pass

    def _send_telegram(self, message: str):
        # Implémentation de l'envoi Telegram
        pass