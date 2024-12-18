import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class AdvancedLogger:
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.setup_logging()

    def setup_logging(self):
        """Configure le système de logging avancé"""
        # Création des dossiers de logs
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        # Logger principal
        self.logger = logging.getLogger(self.app_name)
        self.logger.setLevel(logging.DEBUG)

        # Handler pour les logs généraux
        general_handler = RotatingFileHandler(
            log_dir / 'general.log',
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        general_handler.setLevel(logging.INFO)

        # Handler pour les erreurs
        error_handler = RotatingFileHandler(
            log_dir / 'errors.log',
            maxBytes=10_000_000,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)

        # Handler pour les trades
        trade_handler = RotatingFileHandler(
            log_dir / 'trades.log',
            maxBytes=10_000_000,
            backupCount=5
        )
        trade_handler.setLevel(logging.INFO)

        # Formatage
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        general_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        trade_handler.setFormatter(formatter)

        self.logger.addHandler(general_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(trade_handler)

    def log_trade(self, trade_data: Dict[str, Any]):
        """Enregistre les données d'un trade"""
        try:
            formatted_data = self._format_trade_data(trade_data)
            self.logger.info(f"TRADE: {json.dumps(formatted_data)}")
        except Exception as e:
            self.logger.error(f"Erreur lors du log du trade: {str(e)}")

    def log_strategy(self, strategy_data: Dict[str, Any]):
        """Enregistre les actions d'une stratégie"""
        try:
            formatted_data = self._format_strategy_data(strategy_data)
            self.logger.info(f"STRATEGY: {json.dumps(formatted_data)}")
        except Exception as e:
            self.logger.error(f"Erreur lors du log de la stratégie: {str(e)}")

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Enregistre une erreur avec son contexte"""
        try:
            error_data = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'timestamp': datetime.now().isoformat(),
                'context': context or {}
            }
            self.logger.error(f"ERROR: {json.dumps(error_data)}")
        except Exception as e:
            self.logger.error(f"Erreur lors du log de l'erreur: {str(e)}")
