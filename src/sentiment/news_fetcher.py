"""
News Fetcher Module.

Fetch news from multiple sources for sentiment analysis.
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Represents a single news article."""
    title: str
    source: str
    published_date: datetime
    url: str
    summary: str = ""

    def __repr__(self):
        return f"NewsArticle('{self.title[:50]}...', {self.source}, {self.published_date.strftime('%Y-%m-%d')})"


class NewsFetcher:
    """
    Fetch news from multiple sources.

    Sources:
    1. Yahoo Finance (free, no API key)
    2. Google News (free via web scraping)
    3. NewsAPI.org (optional, requires API key)
    """

    def __init__(self, news_api_key: Optional[str] = None):
        """
        Initialize news fetcher.

        Args:
            news_api_key: Optional NewsAPI.org API key for enhanced news fetching
        """
        self.news_api_key = news_api_key
        logger.info(f"NewsFetcher initialized (NewsAPI: {'Yes' if news_api_key else 'No'})")

    def fetch_news(
        self,
        symbol: str,
        max_results: int = 10,
        days_back: int = 7,
        sources: List[str] = None
    ) -> List[NewsArticle]:
        """
        Fetch news for a stock symbol from multiple sources.

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
            max_results: Maximum number of articles to return
            days_back: How many days back to fetch news
            sources: List of sources to use ['yahoo', 'google', 'newsapi']
                    If None, uses all available sources

        Returns:
            List of NewsArticle objects
        """
        if sources is None:
            sources = ['yahoo', 'google']
            if self.news_api_key:
                sources.append('newsapi')

        all_articles = []

        # Fetch from each source
        if 'yahoo' in sources:
            yahoo_articles = self._fetch_yahoo_news(symbol, max_results)
            all_articles.extend(yahoo_articles)
            logger.debug(f"Fetched {len(yahoo_articles)} articles from Yahoo")

        if 'google' in sources:
            google_articles = self._fetch_google_news(symbol, max_results)
            all_articles.extend(google_articles)
            logger.debug(f"Fetched {len(google_articles)} articles from Google")

        if 'newsapi' in sources and self.news_api_key:
            newsapi_articles = self._fetch_newsapi(symbol, days_back, max_results)
            all_articles.extend(newsapi_articles)
            logger.debug(f"Fetched {len(newsapi_articles)} articles from NewsAPI")

        # Remove duplicates based on title
        unique_articles = self._deduplicate_articles(all_articles)

        # Sort by date (newest first)
        unique_articles.sort(key=lambda x: x.published_date, reverse=True)

        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_articles = [
            article for article in unique_articles
            if article.published_date >= cutoff_date
        ]

        # Limit results
        result = recent_articles[:max_results]

        logger.info(f"Fetched {len(result)} unique news articles for {symbol}")
        return result

    def _fetch_yahoo_news(self, symbol: str, max_results: int) -> List[NewsArticle]:
        """Fetch news from Yahoo Finance."""
        articles = []

        try:
            # Add .NS suffix for Indian stocks
            full_symbol = symbol if symbol.endswith('.NS') else f"{symbol}.NS"

            ticker = yf.Ticker(full_symbol)
            news = ticker.news

            if not news:
                logger.warning(f"No news found for {symbol} on Yahoo Finance")
                return articles

            for item in news[:max_results]:
                try:
                    # Parse Unix timestamp
                    pub_date = datetime.fromtimestamp(item.get('providerPublishTime', 0))

                    article = NewsArticle(
                        title=item.get('title', ''),
                        source='Yahoo Finance',
                        published_date=pub_date,
                        url=item.get('link', ''),
                        summary=item.get('summary', '')
                    )
                    articles.append(article)
                except Exception as e:
                    logger.debug(f"Error parsing Yahoo news item: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching Yahoo news for {symbol}: {e}")

        return articles

    def _fetch_google_news(self, symbol: str, max_results: int) -> List[NewsArticle]:
        """Fetch news from Google News (via web scraping)."""
        articles = []

        try:
            # Search query
            query = f"{symbol} stock news India"
            url = f"https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find news articles
            news_items = soup.find_all('article', limit=max_results)

            for item in news_items:
                try:
                    # Extract title
                    title_elem = item.find('a', class_='JtKRv')
                    if not title_elem:
                        continue

                    title = title_elem.text.strip()
                    link = 'https://news.google.com' + title_elem['href'][1:]  # Remove leading "."

                    # Extract source
                    source_elem = item.find('a', class_='wEwyrc')
                    source = source_elem.text if source_elem else 'Google News'

                    # Extract date (approximate)
                    time_elem = item.find('time')
                    if time_elem and time_elem.get('datetime'):
                        pub_date = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                        # Make timezone-naive
                        pub_date = pub_date.replace(tzinfo=None)
                    else:
                        pub_date = datetime.now()  # Fallback to now

                    article = NewsArticle(
                        title=title,
                        source=f"Google News ({source})",
                        published_date=pub_date,
                        url=link,
                        summary=""
                    )
                    articles.append(article)

                except Exception as e:
                    logger.debug(f"Error parsing Google news item: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching Google news for {symbol}: {e}")

        return articles

    def _fetch_newsapi(self, symbol: str, days_back: int, max_results: int) -> List[NewsArticle]:
        """Fetch news from NewsAPI.org (requires API key)."""
        articles = []

        if not self.news_api_key:
            return articles

        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f"{symbol} stock",
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': max_results,
                'apiKey': self.news_api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('status') == 'ok':
                for item in data.get('articles', []):
                    try:
                        pub_date = datetime.strptime(
                            item['publishedAt'],
                            '%Y-%m-%dT%H:%M:%SZ'
                        )

                        article = NewsArticle(
                            title=item.get('title', ''),
                            source=f"NewsAPI ({item.get('source', {}).get('name', 'Unknown')})",
                            published_date=pub_date,
                            url=item.get('url', ''),
                            summary=item.get('description', '')
                        )
                        articles.append(article)

                    except Exception as e:
                        logger.debug(f"Error parsing NewsAPI item: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error fetching NewsAPI news for {symbol}: {e}")

        return articles

    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on similar titles."""
        seen_titles = set()
        unique_articles = []

        for article in articles:
            # Normalize title for comparison
            normalized_title = article.title.lower().strip()

            # Skip if we've seen a very similar title
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_articles.append(article)

        return unique_articles

    def get_trending_stocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of stocks with most news coverage.

        Args:
            limit: Number of stocks to return

        Returns:
            List of dicts with stock symbol and news count
        """
        # Common Indian stocks
        stocks = [
            'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK',
            'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK'
        ]

        trending = []

        for symbol in stocks:
            news = self.fetch_news(symbol, max_results=5, days_back=1)
            if news:
                trending.append({
                    'symbol': symbol,
                    'news_count': len(news),
                    'latest_news': news[0] if news else None
                })

        # Sort by news count
        trending.sort(key=lambda x: x['news_count'], reverse=True)

        return trending[:limit]
