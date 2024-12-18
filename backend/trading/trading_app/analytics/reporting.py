from typing import Dict, List, Optional

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader
import pdfkit
import yagmail
from concurrent.futures import ThreadPoolExecutor


logging = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    frequency: str  # 'daily', 'weekly', 'monthly'
    metrics: List[str]
    include_charts: bool = True
    include_trades: bool = True
    email_recipients: List[str] = None
    export_format: str = 'pdf'  # 'pdf', 'html', 'excel'


class TradingReportGenerator:
    def __init__(self, config: ReportConfig):
        self.config = config
        self.env = Environment(loader=FileSystemLoader('trading/templates'))
        self.analytics_service = TradingAnalytics()

    async def generate_report(self,
                              start_date: datetime,
                              end_date: datetime) -> Dict:
        """Génère un rapport complet de trading"""
        try:
            # Récupération des données
            trades_data = await self._get_trades_data(start_date, end_date)
            performance_metrics = self.analytics_service.calculate_performance_metrics(
                trades_data
            )
            risk_metrics = self.analytics_service.calculate_risk_metrics(
                trades_data
            )

            # Génération des graphiques
            charts = {}
            if self.config.include_charts:
                charts = await self._generate_charts(trades_data)

            # Création du rapport
            report_data = {
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'performance': performance_metrics,
                'risk': risk_metrics,
                'trades': trades_data if self.config.include_trades else None,
                'charts': charts,
                'recommendations': self._generate_recommendations(
                    performance_metrics,
                    risk_metrics
                )
            }

            # Export du rapport
            report_file = await self._export_report(report_data)

            # Envoi par email si configuré
            if self.config.email_recipients:
                await self._send_report_email(report_file, report_data)

            return report_data

        except Exception as e:
            logging.error(f"Erreur lors de la génération du rapport: {str(e)}")
            raise

    async def _generate_charts(self, trades_data: pd.DataFrame) -> Dict:
        """Génère les visualisations pour le rapport"""
        charts = {}

        # Graphique de l'équité
        equity_chart = go.Figure(data=[
            go.Scatter(
                x=trades_data.index,
                y=trades_data['cumulative_pnl'],
                mode='lines',
                name='Equity Curve'
            )
        ])
        charts['equity'] = equity_chart

        # Distribution des rendements
        returns = trades_data['pnl_percentage']
        returns_chart = go.Figure(data=[
            go.Histogram(
                x=returns,
                nbinsx=50,
                name='Returns Distribution'
            )
        ])
        charts['returns'] = returns_chart

        # Performance par paire de trading
        pair_performance = trades_data.groupby('symbol')['pnl'].sum()
        pair_chart = go.Figure(data=[
            go.Bar(
                x=pair_performance.index,
                y=pair_performance.values,
                name='Pair Performance'
            )
        ])
        charts['pair_performance'] = pair_chart

        return charts

    async def _export_report(self, report_data: Dict) -> str:
        """Exporte le rapport dans le format spécifié"""
        template = self.env.get_template(f'report_{self.config.export_format}.html')
        report_content = template.render(report_data)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if self.config.export_format == 'pdf':
            output_file = f'reports/trading_report_{timestamp}.pdf'
            pdfkit.from_string(report_content, output_file)

        elif self.config.export_format == 'html':
            output_file = f'reports/trading_report_{timestamp}.html'
            with open(output_file, 'w') as f:
                f.write(report_content)

        elif self.config.export_format == 'excel':
            output_file = f'reports/trading_report_{timestamp}.xlsx'
            with pd.ExcelWriter(output_file) as writer:
                pd.DataFrame(report_data['performance']).to_excel(
                    writer,
                    sheet_name='Performance'
                )
                pd.DataFrame(report_data['risk']).to_excel(
                    writer,
                    sheet_name='Risk'
                )
                if report_data['trades'] is not None:
                    report_data['trades'].to_excel(
                        writer,
                        sheet_name='Trades'
                    )

        return output_file

    async def _send_report_email(self, report_file: str,
                                 report_data: Dict) -> None:
        """Envoie le rapport par email"""
        try:
            yag = yagmail.SMTP('your@email.com')

            subject = f"Trading Report - {report_data['period']['start'].date()} to {report_data['period']['end'].date()}"

            contents = [
                "Veuillez trouver ci-joint le rapport de trading.",
                report_file
            ]

            yag.send(
                to=self.config.email_recipients,
                subject=subject,
                contents=contents
            )

        except Exception as e:
            logging.error(f"Erreur lors de l'envoi du rapport par email: {str(e)}")
            raise


class TradingAnalytics:
    """Service d'analyse des performances de trading"""

    def calculate_performance_metrics(self, trades_data: pd.DataFrame) -> Dict:
        """Calcule les métriques de performance"""
        metrics = {}

        # Métriques de base
        metrics['total_trades'] = len(trades_data)
        metrics['winning_trades'] = len(trades_data[trades_data['pnl'] > 0])
        metrics['losing_trades'] = len(trades_data[trades_data['pnl'] < 0])

        metrics['win_rate'] = metrics['winning_trades'] / metrics['total_trades']
        metrics['profit_factor'] = abs(
            trades_data[trades_data['pnl'] > 0]['pnl'].sum() /
            trades_data[trades_data['pnl'] < 0]['pnl'].sum()
        )

        # Rendements
        metrics['total_return'] = trades_data['pnl'].sum()
        metrics['average_return'] = trades_data['pnl'].mean()
        metrics['return_std'] = trades_data['pnl'].std()

        # Ratios
        metrics['sharpe_ratio'] = self._calculate_sharpe_ratio(trades_data)
        metrics['sortino_ratio'] = self._calculate_sortino_ratio(trades_data)
        metrics['calmar_ratio'] = self._calculate_calmar_ratio(trades_data)

        return metrics

    def calculate_risk_metrics(self, trades_data: pd.DataFrame) -> Dict:
        """Calcule les métriques de risque"""
        metrics = {}

        # Drawdown
        cumulative_pnl = trades_data['pnl'].cumsum()
        running_max = cumulative_pnl.expanding().max()
        drawdown = (cumulative_pnl - running_max) / running_max

        metrics['max_drawdown'] = abs(drawdown.min())
        metrics['avg_drawdown'] = abs(drawdown[drawdown < 0].mean())
        metrics['drawdown_duration'] = self._calculate_drawdown_duration(drawdown)

        # Risque
        metrics['var_95'] = self._calculate_var(trades_data, 0.95)
        metrics['var_99'] = self._calculate_var(trades_data, 0.99)
        metrics['expected_shortfall'] = self._calculate_expected_shortfall(
            trades_data
        )

        # Exposition
        metrics['avg_exposure'] = trades_data['exposure'].mean()
        metrics['max_exposure'] = trades_data['exposure'].max()

        return metrics

    def _calculate_var(self, trades_data: pd.DataFrame,
                       confidence: float) -> float:
        """Calcule la Value at Risk"""
        returns = trades_data['pnl_percentage']
        return abs(np.percentile(returns, (1 - confidence) * 100))

    def _calculate_expected_shortfall(self,
                                      trades_data: pd.DataFrame) -> float:
        """Calcule l'Expected Shortfall (CVaR)"""
        returns = trades_data['pnl_percentage']
        var_95 = self._calculate_var(trades_data, 0.95)
        return abs(returns[returns < -var_95].mean())

    def generate_advanced_analytics(self,
                                    trades_data: pd.DataFrame) -> Dict:
        """Génère des analyses avancées"""
        analytics = {}

        # Analyse temporelle
        analytics['time_analysis'] = self._analyze_time_patterns(trades_data)

        # Analyse des corrélations
        analytics['correlations'] = self._analyze_correlations(trades_data)

        # Analyse de la persistance
        analytics['persistence'] = self._analyze_performance_persistence(
            trades_data
        )

        # Analyse des facteurs
        analytics['factors'] = self._analyze_performance_factors(trades_data)

        return analytics

    def _analyze_time_patterns(self, trades_data: pd.DataFrame) -> Dict:
        """Analyse les patterns temporels dans les trades"""
        patterns = {}

        # Performance par jour de la semaine
        patterns['day_of_week'] = trades_data.groupby(
            trades_data.index.dayofweek
        )['pnl'].agg(['mean', 'count', 'sum'])

        # Performance par heure
        patterns['hour_of_day'] = trades_data.groupby(
            trades_data.index.hour
        )['pnl'].agg(['mean', 'count', 'sum'])

        # Performance mensuelle
        patterns['monthly'] = trades_data.groupby(
            [trades_data.index.year, trades_data.index.month]
        )['pnl'].sum()

        return patterns

    def _analyze_correlations(self, trades_data: pd.DataFrame) -> Dict:
        """Analyse les corrélations entre différentes métriques"""
        correlations = {}

        metrics = ['pnl', 'volume', 'duration', 'exposure']
        corr_matrix = trades_data[metrics].corr()

        # Corrélations significatives
        significant_corr = []
        for i in range(len(metrics)):
            for j in range(i + 1, len(metrics)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > 0.3:  # Seuil de significativité
                    significant_corr.append({
                        'metric1': metrics[i],
                        'metric2': metrics[j],
                        'correlation': corr
                    })

        correlations['significant'] = significant_corr
        correlations['matrix'] = corr_matrix

        return correlations

    def _analyze_performance_persistence(self,
                                         trades_data: pd.DataFrame) -> Dict:
        """Analyse la persistance de la performance"""
        persistence = {}

        # Séquences de trades gagnants/perdants
        trades_data['win_streak'] = (
                trades_data['pnl'] > 0
        ).astype(int).groupby(
            (trades_data['pnl'] <= 0).cumsum()
        ).cumsum()

        trades_data['lose_streak'] = (
                trades_data['pnl'] < 0
        ).astype(int).groupby(
            (trades_data['pnl'] >= 0).cumsum()
        ).cumsum()

        persistence['max_win_streak'] = trades_data['win_streak'].max()
        persistence['max_lose_streak'] = trades_data['lose_streak'].max()
        persistence['avg_win_streak'] = trades_data['win_streak'].mean()
        persistence['avg_lose_streak'] = trades_data['lose_streak'].mean()

        return persistence