import re
from typing import List, Dict, Tuple, Any
from textblob import TextBlob
import logging

from ..utils.emoji_sentiment import get_emoji_sentiment, calculate_emoji_sentiment_from_text

logger = logging.getLogger(__name__)


class SentimentService:
    """Service for analyzing sentiment of text and emojis"""
    
    def __init__(self):
        # Pre-compile regex patterns for efficiency
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.mention_pattern = re.compile(r'<@[UW][A-Z0-9]+>')
        self.channel_pattern = re.compile(r'<#[C][A-Z0-9]+\|[^>]+>')
        self.slack_emoji_pattern = re.compile(r':[a-z0-9_-]+:')
        
        # Burnout-related keywords and phrases
        self.burnout_keywords = {
            'exhausted', 'tired', 'overwhelmed', 'stressed', 'burned out', 'burnout',
            'frustrated', 'can\'t handle', 'too much', 'breaking point', 'giving up',
            'done', 'quit', 'leaving', 'fed up', 'had enough', 'overworked',
            'no energy', 'drained', 'worn out', 'at my limit', 'breaking down',
            'can\'t cope', 'falling behind', 'drowning', 'crushed', 'defeated'
        }
        
        # Positive engagement keywords
        self.positive_keywords = {
            'excited', 'love', 'awesome', 'great', 'amazing', 'fantastic',
            'brilliant', 'excellent', 'perfect', 'wonderful', 'outstanding',
            'thrilled', 'delighted', 'happy', 'glad', 'pleased', 'satisfied',
            'motivated', 'inspired', 'energized', 'pumped', 'ready', 'confident'
        }
        
        # Negative sentiment intensifiers
        self.negative_intensifiers = {
            'really', 'very', 'extremely', 'incredibly', 'absolutely', 'totally',
            'completely', 'utterly', 'definitely', 'seriously', 'honestly'
        }
    
    def analyze_text_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text content
        
        Args:
            text: The text to analyze
            
        Returns:
            Sentiment score between -1 and 1
        """
        if not text or not text.strip():
            return 0.0
        
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            if not cleaned_text.strip():
                return 0.0
            
            # Use TextBlob for base sentiment analysis
            blob = TextBlob(cleaned_text)
            base_sentiment = blob.sentiment.polarity
            
            # Apply domain-specific adjustments
            adjusted_sentiment = self._apply_context_adjustments(cleaned_text, base_sentiment)
            
            # Clamp to valid range
            return max(-1.0, min(1.0, adjusted_sentiment))
            
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {e}")
            return 0.0
    
    def analyze_emoji_sentiment(self, text: str) -> float:
        """
        Analyze sentiment based on emojis in text
        
        Args:
            text: The text containing emojis
            
        Returns:
            Sentiment score between -1 and 1, or 0 if no emojis
        """
        try:
            return calculate_emoji_sentiment_from_text(text)
        except Exception as e:
            logger.error(f"Error analyzing emoji sentiment: {e}")
            return 0.0
    
    def get_emoji_sentiment_score(self, emoji: str) -> float:
        """
        Get sentiment score for a specific emoji
        
        Args:
            emoji: The emoji character or name
            
        Returns:
            Sentiment score between -1 and 1
        """
        return get_emoji_sentiment(emoji)
    
    def analyze_combined_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze both text and emoji sentiment
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with text_sentiment, emoji_sentiment, and combined_sentiment
        """
        text_sentiment = self.analyze_text_sentiment(text)
        emoji_sentiment = self.analyze_emoji_sentiment(text)
        
        # Combine sentiments with weighting
        if emoji_sentiment != 0:
            # Give emoji sentiment slightly more weight as it's often more explicit
            combined_sentiment = (text_sentiment * 0.6 + emoji_sentiment * 0.4)
        else:
            combined_sentiment = text_sentiment
        
        return {
            'text_sentiment': text_sentiment,
            'emoji_sentiment': emoji_sentiment,
            'combined_sentiment': combined_sentiment
        }
    
    def detect_burnout_risk(self, text: str) -> Tuple[float, List[str]]:
        """
        Detect potential burnout indicators in text
        
        Args:
            text: The text to analyze
            
        Returns:
            Tuple of (risk_score, matching_keywords)
        """
        if not text:
            return 0.0, []
        
        text_lower = text.lower()
        matching_keywords = []
        risk_score = 0.0
        
        # Check for burnout keywords
        for keyword in self.burnout_keywords:
            if keyword in text_lower:
                matching_keywords.append(keyword)
                base_score = 0.3
                
                # Increase score if combined with intensifiers
                for intensifier in self.negative_intensifiers:
                    if intensifier in text_lower and intensifier in text_lower.split(keyword)[0][-20:]:
                        base_score *= 1.5
                        break
                
                risk_score += base_score
        
        # Additional context analysis
        if any(phrase in text_lower for phrase in ['work life balance', 'mental health', 'taking a break']):
            risk_score += 0.2
        
        if any(phrase in text_lower for phrase in ['weekend work', 'overtime', 'late nights']):
            risk_score += 0.15
        
        # Normalize risk score
        risk_score = min(1.0, risk_score)
        
        return risk_score, matching_keywords
    
    def categorize_sentiment(self, sentiment_score: float) -> str:
        """
        Categorize sentiment score into human-readable categories
        
        Args:
            sentiment_score: Score between -1 and 1
            
        Returns:
            Category string
        """
        if sentiment_score >= 0.6:
            return "very_positive"
        elif sentiment_score >= 0.2:
            return "positive"
        elif sentiment_score >= -0.2:
            return "neutral"
        elif sentiment_score >= -0.6:
            return "negative"
        else:
            return "very_negative"
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text for sentiment analysis
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove URLs
        text = self.url_pattern.sub('', text)
        
        # Remove Slack mentions
        text = self.mention_pattern.sub('', text)
        
        # Remove channel references
        text = self.channel_pattern.sub('', text)
        
        # Remove Slack emoji syntax but keep the emoji names for context
        text = self.slack_emoji_pattern.sub(lambda m: m.group(0)[1:-1], text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _apply_context_adjustments(self, text: str, base_sentiment: float) -> float:
        """
        Apply domain-specific adjustments to sentiment score
        
        Args:
            text: Processed text
            base_sentiment: Base sentiment score from TextBlob
            
        Returns:
            Adjusted sentiment score
        """
        adjusted = base_sentiment
        text_lower = text.lower()
        
        # Boost positive workplace sentiment
        positive_matches = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
        if positive_matches > 0:
            adjusted += positive_matches * 0.1
        
        # Penalize burnout indicators
        burnout_risk, _ = self.detect_burnout_risk(text)
        if burnout_risk > 0:
            adjusted -= burnout_risk * 0.5
        
        # Handle negation patterns
        negation_words = ['not', 'no', 'never', 'none', 'nobody', 'nothing', 'neither', 'nowhere']
        for negation in negation_words:
            if f"{negation} " in text_lower:
                # Find positive words after negation and flip sentiment
                words_after = text_lower.split(f"{negation} ", 1)[1].split()[:5]
                for word in words_after:
                    if word in self.positive_keywords:
                        adjusted -= 0.3
                        break
        
        # Sarcasm detection (basic)
        if any(phrase in text_lower for phrase in ['oh great', 'just great', 'perfect', 'wonderful']) and base_sentiment > 0.3:
            # Likely sarcasm, flip positive to negative
            adjusted = -abs(adjusted) * 0.7
        
        return adjusted
    
    def batch_analyze_sentiment(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Analyze sentiment for multiple texts efficiently
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        results = []
        for text in texts:
            result = self.analyze_combined_sentiment(text)
            results.append(result)
        
        return results
    
    def get_sentiment_insights(self, sentiments: List[float]) -> Dict[str, Any]:
        """
        Get insights from a collection of sentiment scores
        
        Args:
            sentiments: List of sentiment scores
            
        Returns:
            Dictionary of insights
        """
        if not sentiments:
            return {}
        
        # Basic statistics
        avg_sentiment = sum(sentiments) / len(sentiments)
        min_sentiment = min(sentiments)
        max_sentiment = max(sentiments)
        
        # Calculate variance and standard deviation
        variance = sum((s - avg_sentiment) ** 2 for s in sentiments) / len(sentiments)
        std_dev = variance ** 0.5
        
        # Categorize sentiments
        positive_count = sum(1 for s in sentiments if s > 0.1)
        neutral_count = sum(1 for s in sentiments if -0.1 <= s <= 0.1)
        negative_count = sum(1 for s in sentiments if s < -0.1)
        
        # Calculate sentiment trend (if we have chronological data)
        trend = "stable"
        if len(sentiments) >= 3:
            recent_avg = sum(sentiments[-3:]) / 3
            earlier_avg = sum(sentiments[:-3]) / len(sentiments[:-3]) if len(sentiments) > 3 else avg_sentiment
            
            if recent_avg - earlier_avg > 0.1:
                trend = "improving"
            elif recent_avg - earlier_avg < -0.1:
                trend = "declining"
        
        return {
            'average_sentiment': avg_sentiment,
            'min_sentiment': min_sentiment,
            'max_sentiment': max_sentiment,
            'sentiment_volatility': std_dev,
            'positive_count': positive_count,
            'neutral_count': neutral_count,
            'negative_count': negative_count,
            'total_count': len(sentiments),
            'sentiment_trend': trend,
            'dominant_sentiment': self.categorize_sentiment(avg_sentiment)
        }

