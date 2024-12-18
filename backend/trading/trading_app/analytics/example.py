from datetime import datetime, timedelta

from ..analytics.reporting import ReportConfig, TradingReportGenerator, TradingAnalytics

if __name__ == "__main__":
    # Configuration du rapport
    config = ReportConfig(
        frequency='daily',
        metrics=['performance', 'risk', 'exposure'],
        include_charts=True,
        include_trades=True,
        email_recipients=['trader@example.com'],
        export_format='pdf'
    )

    # Création du générateur de rapports
    report_generator = TradingReportGenerator(config)

    # Génération du rapport
    # start_date = datetime.now() - timedelta(days=30)
    # end_date = datetime.now()
    #
    # report_data = await report_generator.generate_report(
    #     start_date,
    #     end_date
    # )
    #
    # # Analyse avancée
    # analytics_service = TradingAnalytics()
    # advanced_analytics = analytics_service.generate_advanced_analytics(
    #     trades_data
    # )