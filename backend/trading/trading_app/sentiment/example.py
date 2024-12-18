from .data_collectors import SentimentAnalyzer, AlternativeDataCollector, \
    SentimentBasedTrading

if __name__ == "__main__":
    # Configuration
    config = {
        'twitter': {
            'consumer_key': 'your_key',
            'consumer_secret': 'your_secret',
            'access_token': 'your_token',
            'access_token_secret': 'your_token_secret'
        },
        'reddit': {
            'client_id': 'your_client_id',
            'client_secret': 'your_client_secret',
            'user_agent': 'your_user_agent'
        },
        'news_api': {
            'api_key': 'your_api_key'
        }
    }

    # Initialisation des analyseurs
    sentiment_analyzer = SentimentAnalyzer(config)
    alt_data_collector = AlternativeDataCollector(config)
    sentiment_trader = SentimentBasedTrading(
        sentiment_analyzer,
        alt_data_collector
    )

    # Génération des signaux
    # signal = await sentiment_trader.generate_trading_signals(
    #     'BTC',
    #     market_data
    # )

    print("Signal de trading:", signal)