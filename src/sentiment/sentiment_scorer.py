"""
Sentiment Scorer Module.

Combines news fetching and sentiment analysis for stocks.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .news_fetcher import NewsFetcher, NewsArticle
from .sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class StockSentiment:
    """Complete sentiment analysis for a stock."""
    symbol: str
    overall_score: float  # -1.0 to +1.0
    overall_sentiment: str  # 'positive', 'negative', 'neutral'
    confidence: float  # 0.0 to 1.0
    news_count: int
    positive_news: int
    negative_news: int
    neutral_news: int
    analyzed_at: datetime
    news_articles: List[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['analyzed_at'] = self.analyzed_at.isoformat()
        return data

    def __repr__(self):
        return (
            f"StockSentiment({self.symbol}: {self.overall_sentiment.upper()}, "
            f"score={self.overall_score:.2f}, news={self.news_count})"
        )


class SentimentScorer:
    """
    Complete sentiment scoring for stocks.

    Fetches news and analyzes sentiment in one go.
    """

    def __init__(
        self,
        news_api_key: Optional[str] = None,
        sentiment_method: str = 'vader'
    ):
        """
        Initialize sentiment scorer.

        Args:
            news_api_key: Optional NewsAPI.org API key
            sentiment_method: 'vader', 'textblob', or 'combined'
        """
        self.news_fetcher = NewsFetcher(news_api_key=news_api_key)
        self.sentiment_analyzer = SentimentAnalyzer(method=sentiment_method)

        logger.info(
            f"SentimentScorer initialized (method: {sentiment_method}, "
            f"NewsAPI: {'Yes' if news_api_key else 'No'})"
        )

    def analyze_stock(
        self,
        symbol: str,
        max_news: int = 20,
        days_back: int = 7
    ) -> StockSentiment:
        """
        Analyze sentiment for a stock.

        Args:
            symbol: Stock symbol
            max_news: Maximum news articles to fetch
            days_back: Days back to look for news

        Returns:
            StockSentiment object with complete analysis
        """
        logger.info(f"Analyzing sentiment for {symbol}...")

        # Fetch news
        news_articles = self.news_fetcher.fetch_news(
            symbol=symbol,
            max_results=max_news,
            days_back=days_back
        )

        if not news_articles:
            logger.warning(f"No news found for {symbol}")
            return StockSentiment(
                symbol=symbol,
                overall_score=0.0,
                overall_sentiment='neutral',
                confidence=0.0,
                news_count=0,
                positive_news=0,
                negative_news=0,
                neutral_news=0,
                analyzed_at=datetime.now(),
                news_articles=[]
            )

        # Analyze sentiment for each article
        analyzed_articles = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_score = 0.0
        total_confidence = 0.0

        for article in news_articles:
            # Analyze title and summary
            combined_text = f"{article.title}. {article.summary}"
            sentiment = self.sentiment_analyzer.analyze_text(combined_text)

            # Count sentiment types
            if sentiment.sentiment == 'positive':
                positive_count += 1
            elif sentiment.sentiment == 'negative':
                negative_count += 1
            else:
                neutral_count += 1

            # Accumulate scores
            total_score += sentiment.score
            total_confidence += sentiment.confidence

            # Store analyzed article
            analyzed_articles.append({
                'title': article.title,
                'source': article.source,
                'date': article.published_date.isoformat(),
                'url': article.url,
                'sentiment': sentiment.sentiment,
                'score': sentiment.score,
                'confidence': sentiment.confidence
            })

        # Calculate overall metrics
        avg_score = total_score / len(news_articles)
        avg_confidence = total_confidence / len(news_articles)

        # Determine overall sentiment
        if avg_score > 0.1:
            overall_sentiment = 'positive'
        elif avg_score < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        result = StockSentiment(
            symbol=symbol,
            overall_score=avg_score,
            overall_sentiment=overall_sentiment,
            confidence=avg_confidence,
            news_count=len(news_articles),
            positive_news=positive_count,
            negative_news=negative_count,
            neutral_news=neutral_count,
            analyzed_at=datetime.now(),
            news_articles=analyzed_articles
        )

        logger.info(
            f"Sentiment for {symbol}: {overall_sentiment.upper()} "
            f"(score: {avg_score:.2f}, news: {len(news_articles)})"
        )

        return result

    def compare_stocks(
        self,
        symbols: List[str],
        max_news: int = 10,
        days_back: int = 7
    ) -> List[StockSentiment]:
        """
        Compare sentiment across multiple stocks.

        Args:
            symbols: List of stock symbols
            max_news: Max news per stock
            days_back: Days back to look

        Returns:
            List of StockSentiment, sorted by sentiment score
        """
        results = []

        for symbol in symbols:
            try:
                sentiment = self.analyze_stock(symbol, max_news, days_back)
                results.append(sentiment)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue

        # Sort by sentiment score (most positive first)
        results.sort(key=lambda x: x.overall_score, reverse=True)

        return results

    def get_sentiment_summary(self, sentiment: StockSentiment) -> Dict[str, Any]:
        """
        Get human-readable sentiment summary.

        Args:
            sentiment: StockSentiment object

        Returns:
            Dict with summary statistics and recommendations
        """
        # Determine strength
        if abs(sentiment.overall_score) > 0.5:
            strength = "Strong"
        elif abs(sentiment.overall_score) > 0.2:
            strength = "Moderate"
        else:
            strength = "Weak"

        # Generate recommendation
        if sentiment.overall_sentiment == 'positive' and sentiment.overall_score > 0.3:
            recommendation = "Consider BUYING - Positive news sentiment"
            signal = "BUY"
        elif sentiment.overall_sentiment == 'negative' and sentiment.overall_score < -0.3:
            recommendation = "Consider SELLING/AVOIDING - Negative news sentiment"
            signal = "SELL"
        else:
            recommendation = "NEUTRAL - Mixed or weak news sentiment"
            signal = "HOLD"

        # Calculate sentiment distribution
        total = sentiment.news_count
        if total > 0:
            pos_pct = (sentiment.positive_news / total) * 100
            neg_pct = (sentiment.negative_news / total) * 100
            neu_pct = (sentiment.neutral_news / total) * 100
        else:
            pos_pct = neg_pct = neu_pct = 0

        return {
            'symbol': sentiment.symbol,
            'sentiment': sentiment.overall_sentiment.upper(),
            'strength': strength,
            'score': sentiment.overall_score,
            'confidence': sentiment.confidence,
            'signal': signal,
            'recommendation': recommendation,
            'news_count': sentiment.news_count,
            'distribution': {
                'positive': pos_pct,
                'negative': neg_pct,
                'neutral': neu_pct
            },
            'latest_news_count': min(sentiment.news_count, 5),
            'analyzed_at': sentiment.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def filter_by_sentiment(
        self,
        symbols: List[str],
        target_sentiment: str = 'positive',
        min_confidence: float = 0.3,
        max_news: int = 10
    ) -> List[StockSentiment]:
        """
        Filter stocks by sentiment.

        Args:
            symbols: List of stock symbols to check
            target_sentiment: 'positive' or 'negative'
            min_confidence: Minimum confidence threshold
            max_news: Max news to fetch per stock

        Returns:
            List of stocks matching sentiment criteria
        """
        results = []

        for symbol in symbols:
            try:
                sentiment = self.analyze_stock(symbol, max_news=max_news)

                # Check if matches criteria
                if (sentiment.overall_sentiment == target_sentiment and
                    sentiment.confidence >= min_confidence):
                    results.append(sentiment)

            except Exception as e:
                logger.error(f"Error filtering {symbol}: {e}")
                continue

        # Sort by confidence (highest first)
        results.sort(key=lambda x: x.confidence, reverse=True)

        return results
