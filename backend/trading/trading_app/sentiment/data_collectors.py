from typing import Dict, List, Optional

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tweepy
import praw
import newsapi
from bs4 import BeautifulSoup
import requests
import aiohttp
import asyncio
from dataclasses import dataclass
import json

logger = logging.getLogger('__name__')


@dataclass
class SentimentData:
    timestamp: datetime
    source: str
    text: str
    sentiment_score: float
    relevance_score: float
    entity: str
    metadata: Dict


class SentimentAnalyzer:
    def __init__(self, config: Dict):
        self.config = config
        # Initialisation des APIs
        self.twitter_api = self._init_twitter_api()
        self.reddit_api = self._init_reddit_api()
        self.news_api = self._init_news_api()

    def _init_twitter_api(self) -> tweepy.API:
        """Initialise l'API Twitter"""
        auth = tweepy.OAuthHandler(
            self.config['twitter']['consumer_key'],
            self.config['twitter']['consumer_secret']
        )
        auth.set_access_token(
            self.config['twitter']['access_token'],
            self.config['twitter']['access_token_secret']
        )
        return tweepy.API(auth)

    def _init_reddit_api(self) -> praw.Reddit:
        """Initialise l'API Reddit"""
        return praw.Reddit(
            client_id=self.config['reddit']['client_id'],
            client_secret=self.config['reddit']['client_secret'],
            user_agent=self.config['reddit']['user_agent']
        )

    def _init_news_api(self) -> newsapi.NewsApiClient:
        """Initialise l'API News"""
        return newsapi.NewsApiClient(api_key=self.config['news_api']['api_key'])

    async def collect_sentiment_data(self,
                                     symbol: str,
                                     lookback_hours: int = 24) -> List[SentimentData]:
        """Collecte les données de sentiment de toutes les sources"""
        tasks = [
            self.collect_twitter_sentiment(symbol, lookback_hours),
            self.collect_reddit_sentiment(symbol, lookback_hours),
            self.collect_news_sentiment(symbol, lookback_hours),
            self.collect_crypto_fear_greed()
        ]

        results = await asyncio.gather(*tasks)

        # Fusion des résultats
        all_sentiment_data = []
        for result in results:
            all_sentiment_data.extend(result)

        return all_sentiment_data

    async def collect_twitter_sentiment(self,
                                        symbol: str,
                                        lookback_hours: int) -> List[SentimentData]:
        """Collecte et analyse les sentiments depuis Twitter"""
        sentiment_data = []

        try:
            # Recherche des tweets
            query = f"#{symbol} OR ${symbol}"
            tweets = self.twitter_api.search_tweets(
                q=query,
                lang="en",
                count=100,
                result_type="recent"
            )

            for tweet in tweets:
                # Analyse du sentiment
                sentiment_score = await self._analyze_text_sentiment(tweet.text)
                # Calcul de la pertinence
                relevance_score = self._calculate_relevance(
                    tweet.text,
                    tweet.user.followers_count,
                    tweet.retweet_count,
                    tweet.favorite_count
                )

                sentiment_data.append(
                    SentimentData(
                        timestamp=tweet.created_at,
                        source='twitter',
                        text=tweet.text,
                        sentiment_score=sentiment_score,
                        relevance_score=relevance_score,
                        entity=symbol,
                        metadata={
                            'followers': tweet.user.followers_count,
                            'retweets': tweet.retweet_count,
                            'likes': tweet.favorite_count
                        }
                    )
                )

        except Exception as e:
            logging.error(f"Erreur lors de la collecte Twitter: {str(e)}")

        return sentiment_data

    async def collect_reddit_sentiment(self,
                                       symbol: str,
                                       lookback_hours: int) -> List[SentimentData]:
        """Collecte et analyse les sentiments depuis Reddit"""
        sentiment_data = []
        subreddits = ['cryptocurrency', 'bitcoin', 'CryptoMarkets']

        try:
            for subreddit_name in subreddits:
                subreddit = self.reddit_api.subreddit(subreddit_name)
                posts = subreddit.search(
                    symbol,
                    time_filter='day',
                    sort='relevance'
                )

                for post in posts:
                    # Analyse du sentiment
                    sentiment_score = await self._analyze_text_sentiment(
                        post.title + " " + post.selftext
                    )

                    # Calcul de la pertinence
                    relevance_score = self._calculate_relevance(
                        post.title,
                        post.score,
                        post.num_comments,
                        post.upvote_ratio
                    )

                    sentiment_data.append(
                        SentimentData(
                            timestamp=datetime.fromtimestamp(post.created_utc),
                            source='reddit',
                            text=post.title,
                            sentiment_score=sentiment_score,
                            relevance_score=relevance_score,
                            entity=symbol,
                            metadata={
                                'score': post.score,
                                'comments': post.num_comments,
                                'upvote_ratio': post.upvote_ratio
                            }
                        )
                    )

        except Exception as e:
            logging.error(f"Erreur lors de la collecte Reddit: {str(e)}")

        return sentiment_data

    async def collect_news_sentiment(self,
                                     symbol: str,
                                     lookback_hours: int) -> List[SentimentData]:
        """Collecte et analyse les sentiments depuis les news"""
        sentiment_data = []

        try:
            news = self.news_api.get_everything(
                q=symbol,
                language='en',
                sort_by='relevancy',
                from_param=(
                        datetime.now() - timedelta(hours=lookback_hours)
                ).strftime('%Y-%m-%d')
            )

            for article in news['articles']:
                # Analyse du sentiment
                sentiment_score = await self._analyze_text_sentiment(
                    article['title'] + " " + (article['description'] or "")
                )

                # Calcul de la pertinence
                relevance_score = self._calculate_news_relevance(article)

                sentiment_data.append(
                    SentimentData(
                        timestamp=datetime.strptime(
                            article['publishedAt'],
                            '%Y-%m-%dT%H:%M:%SZ'
                        ),
                        source='news',
                        text=article['title'],
                        sentiment_score=sentiment_score,
                        relevance_score=relevance_score,
                        entity=symbol,
                        metadata={
                            'source': article['source']['name'],
                            'url': article['url'],
                            'author': article['author']
                        }
                    )
                )

        except Exception as e:
            logging.error(f"Erreur lors de la collecte News: {str(e)}")

        return sentiment_data

    async def collect_crypto_fear_greed(self) -> List[SentimentData]:
        """Collecte l'index Fear & Greed"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        'https://api.alternative.me/fng/'
                ) as response:
                    data = await response.json()

                    return [SentimentData(
                        timestamp=datetime.now(),
                        source='fear_greed_index',
                        text='',
                        sentiment_score=int(data['data'][0]['value']) / 100,
                        relevance_score=1.0,
                        entity='MARKET',
                        metadata={
                            'classification': data['data'][0]['value_classification']
                        }
                    )]

        except Exception as e:
            logging.error(f"Erreur lors de la collecte Fear & Greed: {str(e)}")
            return []

    async def _analyze_text_sentiment(self, text: str) -> float:
        """Analyse le sentiment d'un texte"""
        try:
            # Utilisation de VADER pour l'analyse de sentiment
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()

            # Calcul du score de sentiment
            sentiment_dict = analyzer.polarity_scores(text)

            # Normalisation du score composite entre 0 et 1
            return (sentiment_dict['compound'] + 1) / 2

        except Exception as e:
            logging.error(f"Erreur lors de l'analyse de sentiment: {str(e)}")
            return 0.5


class AlternativeDataCollector:
    def __init__(self, config: Dict):
        self.config = config

    async def collect_blockchain_data(self,
                                      symbol: str,
                                      lookback_hours: int = 24) -> pd.DataFrame:
        """Collecte les données on-chain"""
        try:
            # Récupération des données blockchain
            async with aiohttp.ClientSession() as session:
                blockchain_data = await asyncio.gather(
                    self._get_network_data(session, symbol),
                    self._get_wallet_data(session, symbol),
                    self._get_mining_data(session, symbol)
                )

            return pd.DataFrame(blockchain_data)

        except Exception as e:
            logging.error(f"Erreur lors de la collecte blockchain: {str(e)}")
            return pd.DataFrame()

    async def collect_trading_data(self,
                                   symbol: str,
                                   lookback_hours: int = 24) -> pd.DataFrame:
        """Collecte les données de trading avancées"""
        try:
            async with aiohttp.ClientSession() as session:
                trading_data = await asyncio.gather(
                    self._get_order_book_data(session, symbol),
                    self._get_funding_rates(session, symbol),
                    self._get_liquidations(session, symbol)
                )

            return pd.DataFrame(trading_data)

        except Exception as e:
            logging.error(f"Erreur lors de la collecte trading: {str(e)}")
            return pd.DataFrame()


class SentimentBasedTrading:
    def __init__(self,
                 sentiment_analyzer: SentimentAnalyzer,
                 alt_data_collector: AlternativeDataCollector):
        self.sentiment_analyzer = sentiment_analyzer
        self.alt_data_collector = alt_data_collector

    async def generate_trading_signals(self,
                                       symbol: str,
                                       market_data: pd.DataFrame) -> Dict:
        """Génère des signaux de trading basés sur le sentiment"""
        # Collecte des données
        sentiment_data = await self.sentiment_analyzer.collect_sentiment_data(
            symbol
        )
        blockchain_data = await self.alt_data_collector.collect_blockchain_data(
            symbol
        )
        trading_data = await self.alt_data_collector.collect_trading_data(
            symbol
        )

        # Agrégation des signaux
        sentiment_signal = self._analyze_sentiment_signals(sentiment_data)
        blockchain_signal = self._analyze_blockchain_signals(blockchain_data)
        trading_signal = self._analyze_trading_signals(trading_data)

        # Combinaison des signaux
        combined_signal = self._combine_signals(
            sentiment_signal,
            blockchain_signal,
            trading_signal
        )

        return {
            'signal': combined_signal['direction'],
            'confidence': combined_signal['confidence'],
            'factors': {
                'sentiment': sentiment_signal,
                'blockchain': blockchain_signal,
                'trading': trading_signal
            }
        }
