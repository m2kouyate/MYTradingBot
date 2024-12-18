from decimal import Decimal
from typing import Dict, List


class RiskManagement:
    def __init__(self, config: Dict):
        self.max_position_size = config.get('max_position_size', 0.1)
        self.max_open_positions = config.get('max_open_positions', 3)
        self.daily_loss_limit = config.get('daily_loss_limit', 0.03)
        self.total_portfolio_value = 0

    def calculate_position_size(self,
                                current_portfolio_value: Decimal,
                                risk_per_trade: Decimal) -> Decimal:
        """Calcule la taille de position optimale selon Kelly Criterion"""
        self.total_portfolio_value = current_portfolio_value
        max_position = current_portfolio_value * self.max_position_size
        kelly_size = self._kelly_criterion(risk_per_trade)
        return min(max_position, kelly_size)

    def _kelly_criterion(self, risk_per_trade: Decimal) -> Decimal:
        """Implémentation du critère de Kelly pour le sizing"""
        win_rate = 0.55  # À ajuster selon la performance historique
        risk_reward = 2  # Ratio risque/récompense cible

        kelly_percentage = win_rate - (1 - win_rate) / risk_reward
        return self.total_portfolio_value * Decimal(str(kelly_percentage))

    def check_risk_limits(self,
                          current_positions: List[Dict],
                          daily_pnl: Decimal) -> bool:
        """Vérifie si les limites de risque sont respectées"""
        # Vérification du nombre de positions ouvertes
        if len(current_positions) >= self.max_open_positions:
            return False

        # Vérification de la limite de perte journalière
        if daily_pnl < -self.total_portfolio_value * self.daily_loss_limit:
            return False

        return True