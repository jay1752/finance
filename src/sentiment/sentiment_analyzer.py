"""
Sentiment Analyzer Module.

Analyze sentiment of news articles using VADER and TextBlob.
"""
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

# Try to import sentiment libraries (will install in requirements if needed)
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    logger.warning("VADER not available. Install with: pip install vaderSentiment")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logger.warning("TextBlob not available. Install with: pip install textblob")


@dataclass
class SentimentScore:
    """Sentiment score for a text."""
    score: float  # -1.0 (very negative) to +1.0 (very positive)
    sentiment: str  # 'positive', 'negative', or 'neutral'
    confidence: float  # 0.0 to 1.0
    method: str  # 'vader' or 'textblob' or 'combined'
    breakdown: Dict[str, float] = None  # Detailed scores

    def __repr__(self):
        return f"Sentiment({self.sentiment}, score={self.score:.2f}, confidence={self.confidence:.2f})"


class SentimentAnalyzer:
    """
    Analyze sentiment using multiple methods.

    Methods:
    - VADER: Best for news/social media (recommended)
    - TextBlob: General purpose sentiment analysis
    - Combined: Average of both methods
    """

    def __init__(self, method: str = 'vader'):
        """
        Initialize sentiment analyzer.

        Args:
            method: 'vader', 'textblob', or 'combined'
        """
        self.method = method

        # Initialize VADER
        if VADER_AVAILABLE:
            self.vader = SentimentIntensityAnalyzer()
        else:
            self.vader = None
            if method == 'vader':
                logger.error("VADER requested but not available!")

        logger.info(f"SentimentAnalyzer initialized with method: {method}")

    def analyze_text(self, text: str) -> SentimentScore:
        """
        Analyze sentiment of a text.

        Args:
            text: Text to analyze (headline, summary, etc.)

        Returns:
            SentimentScore object
        """
        if not text or not text.strip():
            return SentimentScore(
                score=0.0,
                sentiment='neutral',
                confidence=0.0,
                method='none'
            )

        # Choose method
        if self.method == 'vader':
            return self._analyze_vader(text)
        elif self.method == 'textblob':
            return self._analyze_textblob(text)
        elif self.method == 'combined':
            return self._analyze_combined(text)
        else:
            raise ValueError(f"Unknown method: {self.method}")

    def _analyze_vader(self, text: str) -> SentimentScore:
        """Analyze using VADER."""
        if not VADER_AVAILABLE or self.vader is None:
            logger.warning("VADER not available, falling back to TextBlob")
            return self._analyze_textblob(text)

        # Get VADER scores
        scores = self.vader.polarity_scores(text)

        # VADER returns:
        # - neg: negative score (0-1)
        # - neu: neutral score (0-1)
        # - pos: positive score (0-1)
        # - compound: overall score (-1 to +1)

        compound = scores['compound']

        # Classify sentiment
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        # Calculate confidence (based on how far from neutral)
        confidence = abs(compound)

        return SentimentScore(
            score=compound,
            sentiment=sentiment,
            confidence=confidence,
            method='vader',
            breakdown={
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu']
            }
        )

    def _analyze_textblob(self, text: str) -> SentimentScore:
        """Analyze using TextBlob."""
        if not TEXTBLOB_AVAILABLE:
            # Fallback to simple keyword-based analysis
            return self._analyze_simple(text)

        # Get TextBlob sentiment
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to +1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1

        # Classify sentiment
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        # Confidence is inverse of subjectivity (more objective = more confident)
        # Also factor in strength of polarity
        confidence = (1 - subjectivity) * abs(polarity)

        return SentimentScore(
            score=polarity,
            sentiment=sentiment,
            confidence=confidence,
            method='textblob',
            breakdown={
                'polarity': polarity,
                'subjectivity': subjectivity
            }
        )

    def _analyze_combined(self, text: str) -> SentimentScore:
        """Analyze using both methods and combine."""
        vader_score = self._analyze_vader(text)
        textblob_score = self._analyze_textblob(text)

        # Average the scores
        combined_score = (vader_score.score + textblob_score.score) / 2

        # Classify
        if combined_score > 0.1:
            sentiment = 'positive'
        elif combined_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        # Average confidence
        combined_confidence = (vader_score.confidence + textblob_score.confidence) / 2

        return SentimentScore(
            score=combined_score,
            sentiment=sentiment,
            confidence=combined_confidence,
            method='combined',
            breakdown={
                'vader_score': vader_score.score,
                'textblob_score': textblob_score.score,
                'vader_sentiment': vader_score.sentiment,
                'textblob_sentiment': textblob_score.sentiment
            }
        )

    def _analyze_simple(self, text: str) -> SentimentScore:
        """
        Simple keyword-based sentiment analysis.

        Fallback when libraries aren't available.
        """
        text_lower = text.lower()

        # Positive keywords
        positive_words = [
            'profit', 'growth', 'gain', 'up', 'rise', 'high', 'surge',
            'boost', 'strong', 'positive', 'success', 'win', 'beat',
            'exceed', 'bullish', 'rally', 'upgrade', 'buy'
        ]

        # Negative keywords
        negative_words = [
            'loss', 'decline', 'fall', 'down', 'drop', 'low', 'crash',
            'weak', 'negative', 'fail', 'miss', 'below', 'bearish',
            'sell', 'downgrade', 'warning', 'risk', 'concern'
        ]

        # Count occurrences
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        # Calculate score
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
            sentiment = 'neutral'
            confidence = 0.0
        else:
            score = (positive_count - negative_count) / total
            if score > 0.2:
                sentiment = 'positive'
            elif score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            confidence = min(total / 10, 1.0)  # More keywords = more confident

        return SentimentScore(
            score=score,
            sentiment=sentiment,
            confidence=confidence,
            method='simple_keywords',
            breakdown={
                'positive_words': positive_count,
                'negative_words': negative_count
            }
        )

    def analyze_headlines(self, headlines: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple headlines and aggregate.

        Args:
            headlines: List of headline texts

        Returns:
            Dict with aggregate sentiment statistics
        """
        if not headlines:
            return {
                'avg_score': 0.0,
                'overall_sentiment': 'neutral',
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'confidence': 0.0
            }

        scores = [self.analyze_text(headline) for headline in headlines]

        # Calculate statistics
        avg_score = sum(s.score for s in scores) / len(scores)
        avg_confidence = sum(s.confidence for s in scores) / len(scores)

        positive_count = sum(1 for s in scores if s.sentiment == 'positive')
        negative_count = sum(1 for s in scores if s.sentiment == 'negative')
        neutral_count = sum(1 for s in scores if s.sentiment == 'neutral')

        # Overall sentiment
        if avg_score > 0.1:
            overall_sentiment = 'positive'
        elif avg_score < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        return {
            'avg_score': avg_score,
            'overall_sentiment': overall_sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'confidence': avg_confidence,
            'total_headlines': len(headlines),
            'individual_scores': scores
        }

    def get_financial_keywords(self, text: str) -> Dict[str, List[str]]:
        """
        Extract financial keywords from text.

        Returns:
            Dict with lists of positive and negative financial terms found
        """
        text_lower = text.lower()

        # Financial positive terms
        positive_financial = [
            'profit', 'revenue growth', 'earnings beat', 'dividend increase',
            'market share gain', 'expansion', 'acquisition', 'partnership',
            'innovation', 'breakthrough', 'record high', 'strong demand'
        ]

        # Financial negative terms
        negative_financial = [
            'loss', 'revenue decline', 'earnings miss', 'dividend cut',
            'market share loss', 'layoff', 'restructuring', 'debt',
            'investigation', 'lawsuit', 'recall', 'weak demand'
        ]

        found_positive = [term for term in positive_financial if term in text_lower]
        found_negative = [term for term in negative_financial if term in text_lower]

        return {
            'positive_keywords': found_positive,
            'negative_keywords': found_negative
        }
