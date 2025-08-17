from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import json
import logging

from ..models.database import (
    MonitoredChannel, Message, DailyStats, TeamInsight, 
    UserMetrics, get_db
)
from ..config import settings
from .sentiment_service import SentimentService

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analyzing team engagement and generating insights"""
    
    def __init__(self):
        self.sentiment_service = SentimentService()
    
    def generate_daily_stats(self, target_date: Optional[date] = None) -> None:
        """
        Generate daily statistics for all monitored channels
        
        Args:
            target_date: Date to generate stats for (defaults to today)
        """
        if target_date is None:
            target_date = datetime.utcnow().date()
        
        db = next(get_db())
        try:
            channels = db.query(MonitoredChannel).filter(MonitoredChannel.is_active == True).all()
            
            for channel in channels:
                self._generate_channel_daily_stats(channel, target_date, db)
            
            db.commit()
            logger.info(f"Generated daily stats for {target_date}")
            
        except Exception as e:
            logger.error(f"Error generating daily stats: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _generate_channel_daily_stats(self, channel: MonitoredChannel, target_date: date, db: Session):
        """Generate daily stats for a specific channel"""
        try:
            # Check if stats already exist for this date
            existing_stats = db.query(DailyStats).filter(
                and_(
                    DailyStats.channel_id == channel.channel_id,
                    func.date(DailyStats.date) == target_date
                )
            ).first()
            
            if existing_stats:
                return  # Skip if already processed
            
            # Get messages for the target date
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = start_datetime + timedelta(days=1)
            
            messages = db.query(Message).filter(
                and_(
                    Message.channel_id == channel.channel_id,
                    Message.timestamp >= start_datetime,
                    Message.timestamp < end_datetime
                )
            ).all()
            
            if not messages:
                return
            
            # Calculate metrics
            message_count = len(messages)
            unique_users = len(set(msg.user_id for msg in messages))
            
            sentiments = [msg.overall_sentiment for msg in messages if msg.overall_sentiment is not None]
            
            if sentiments:
                avg_sentiment = sum(sentiments) / len(sentiments)
                min_sentiment = min(sentiments)
                max_sentiment = max(sentiments)
                
                # Categorize sentiments
                positive_count = sum(1 for s in sentiments if s > 0.1)
                neutral_count = sum(1 for s in sentiments if -0.1 <= s <= 0.1)
                negative_count = sum(1 for s in sentiments if s < -0.1)
            else:
                avg_sentiment = min_sentiment = max_sentiment = 0.0
                positive_count = neutral_count = negative_count = 0
            
            # Calculate engagement metrics
            total_reactions = sum(msg.reaction_count for msg in messages)
            thread_count = sum(1 for msg in messages if msg.has_thread)
            
            # Response rate calculation
            messages_with_engagement = sum(1 for msg in messages if msg.reaction_count > 0 or msg.has_thread)
            response_rate = messages_with_engagement / message_count if message_count > 0 else 0.0
            
            # Create daily stats record
            daily_stats = DailyStats(
                channel_id=channel.channel_id,
                date=start_datetime,
                message_count=message_count,
                unique_users=unique_users,
                avg_sentiment=avg_sentiment,
                min_sentiment=min_sentiment,
                max_sentiment=max_sentiment,
                positive_count=positive_count,
                neutral_count=neutral_count,
                negative_count=negative_count,
                total_reactions=total_reactions,
                thread_count=thread_count,
                response_rate=response_rate
            )
            
            db.add(daily_stats)
            
        except Exception as e:
            logger.error(f"Error generating daily stats for channel {channel.channel_id}: {e}")
    
    def generate_weekly_insights(self, week_start: Optional[date] = None) -> TeamInsight:
        """
        Generate team insights for a week
        
        Args:
            week_start: Start of the week (defaults to current Monday)
            
        Returns:
            Generated team insight
        """
        if week_start is None:
            today = datetime.utcnow().date()
            week_start = today - timedelta(days=today.weekday())  # Current Monday
        
        week_end = week_start + timedelta(days=6)
        
        db = next(get_db())
        try:
            # Get all daily stats for the week
            daily_stats = db.query(DailyStats).filter(
                and_(
                    func.date(DailyStats.date) >= week_start,
                    func.date(DailyStats.date) <= week_end
                )
            ).all()
            
            if not daily_stats:
                logger.warning(f"No daily stats found for week {week_start}")
                return None
            
            # Calculate weekly metrics
            weekly_metrics = self._calculate_weekly_metrics(daily_stats, db, week_start, week_end)
            
            # Generate insights and recommendations
            insights = self._generate_actionable_insights(weekly_metrics, daily_stats, db)
            
            # Check if insight already exists
            existing_insight = db.query(TeamInsight).filter(
                func.date(TeamInsight.week_start) == week_start
            ).first()
            
            if existing_insight:
                # Update existing insight
                for key, value in weekly_metrics.items():
                    setattr(existing_insight, key, value)
                for key, value in insights.items():
                    setattr(existing_insight, key, value)
                team_insight = existing_insight
            else:
                # Create new insight
                team_insight = TeamInsight(
                    week_start=datetime.combine(week_start, datetime.min.time()),
                    week_end=datetime.combine(week_end, datetime.max.time()),
                    **weekly_metrics,
                    **insights
                )
                db.add(team_insight)
            
            db.commit()
            db.refresh(team_insight)
            
            return team_insight
            
        except Exception as e:
            logger.error(f"Error generating weekly insights: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def _calculate_weekly_metrics(self, daily_stats: List[DailyStats], db: Session, 
                                 week_start: date, week_end: date) -> Dict[str, Any]:
        """Calculate aggregated weekly metrics"""
        
        # Overall sentiment analysis
        all_sentiments = []
        for stat in daily_stats:
            if stat.avg_sentiment is not None:
                all_sentiments.append(stat.avg_sentiment)
        
        overall_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0.0
        
        # Sentiment trend analysis
        sentiment_trend = self._calculate_sentiment_trend(daily_stats)
        
        # Engagement level analysis
        total_messages = sum(stat.message_count for stat in daily_stats)
        total_reactions = sum(stat.total_reactions for stat in daily_stats)
        avg_response_rate = sum(stat.response_rate for stat in daily_stats) / len(daily_stats) if daily_stats else 0.0
        
        engagement_level = self._categorize_engagement_level(total_messages, total_reactions, avg_response_rate)
        
        # Burnout risk analysis
        burnout_metrics = self._analyze_burnout_risk(db, week_start, week_end)
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_trend': sentiment_trend,
            'engagement_level': engagement_level,
            'burnout_risk_score': burnout_metrics['risk_score'],
            'burnout_warning': burnout_metrics['warning'],
            'at_risk_users': json.dumps(burnout_metrics['at_risk_users'])
        }
    
    def _calculate_sentiment_trend(self, daily_stats: List[DailyStats]) -> str:
        """Calculate sentiment trend over the week"""
        if len(daily_stats) < 3:
            return "stable"
        
        # Sort by date
        sorted_stats = sorted(daily_stats, key=lambda x: x.date)
        sentiments = [stat.avg_sentiment for stat in sorted_stats if stat.avg_sentiment is not None]
        
        if len(sentiments) < 3:
            return "stable"
        
        # Calculate trend using linear regression slope
        n = len(sentiments)
        x_vals = list(range(n))
        y_vals = sentiments
        
        # Simple slope calculation
        x_mean = sum(x_vals) / n
        y_mean = sum(y_vals) / n
        
        numerator = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n))
        denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.05:
            return "improving"
        elif slope < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _categorize_engagement_level(self, total_messages: int, total_reactions: int, avg_response_rate: float) -> str:
        """Categorize overall engagement level"""
        
        # Normalize metrics (these thresholds can be adjusted based on team size)
        message_score = min(1.0, total_messages / 100)  # 100 messages per week = full score
        reaction_score = min(1.0, total_reactions / 50)   # 50 reactions per week = full score
        response_score = avg_response_rate
        
        overall_score = (message_score + reaction_score + response_score) / 3
        
        if overall_score >= 0.7:
            return "high"
        elif overall_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _analyze_burnout_risk(self, db: Session, week_start: date, week_end: date) -> Dict[str, Any]:
        """Analyze burnout risk for the team"""
        
        start_datetime = datetime.combine(week_start, datetime.min.time())
        end_datetime = datetime.combine(week_end, datetime.max.time())
        
        # Get all messages from the week
        messages = db.query(Message).filter(
            and_(
                Message.timestamp >= start_datetime,
                Message.timestamp <= end_datetime,
                Message.overall_sentiment.isnot(None)
            )
        ).all()
        
        if not messages:
            return {'risk_score': 0.0, 'warning': False, 'at_risk_users': []}
        
        # Analyze by user
        user_sentiments = {}
        user_burnout_indicators = {}
        
        for message in messages:
            user_id = message.user_id
            if user_id not in user_sentiments:
                user_sentiments[user_id] = []
                user_burnout_indicators[user_id] = []
            
            user_sentiments[user_id].append(message.overall_sentiment)
            
            # Check for burnout indicators in message text
            burnout_risk, keywords = self.sentiment_service.detect_burnout_risk(message.text)
            if burnout_risk > 0:
                user_burnout_indicators[user_id].append((burnout_risk, keywords))
        
        # Calculate risk for each user
        at_risk_users = []
        total_risk = 0.0
        
        for user_id, sentiments in user_sentiments.items():
            user_avg_sentiment = sum(sentiments) / len(sentiments)
            user_volatility = self._calculate_sentiment_volatility(sentiments)
            
            # Base risk from negative sentiment
            sentiment_risk = max(0, -user_avg_sentiment) * 0.5
            
            # Add volatility risk
            volatility_risk = min(0.3, user_volatility * 0.3)
            
            # Add explicit burnout indicator risk
            burnout_indicator_risk = 0.0
            if user_id in user_burnout_indicators:
                indicators = user_burnout_indicators[user_id]
                if indicators:
                    max_risk = max(risk for risk, _ in indicators)
                    burnout_indicator_risk = max_risk * 0.4
            
            user_risk = sentiment_risk + volatility_risk + burnout_indicator_risk
            user_risk = min(1.0, user_risk)
            
            if user_risk > settings.warning_threshold:
                at_risk_users.append({
                    'user_id': user_id,
                    'risk_score': user_risk,
                    'avg_sentiment': user_avg_sentiment,
                    'message_count': len(sentiments)
                })
            
            total_risk += user_risk
        
        # Calculate team-level risk
        team_risk = total_risk / len(user_sentiments) if user_sentiments else 0.0
        burnout_warning = team_risk > abs(settings.burnout_threshold) or len(at_risk_users) > 0
        
        return {
            'risk_score': team_risk,
            'warning': burnout_warning,
            'at_risk_users': at_risk_users
        }
    
    def _calculate_sentiment_volatility(self, sentiments: List[float]) -> float:
        """Calculate sentiment volatility (standard deviation)"""
        if len(sentiments) < 2:
            return 0.0
        
        mean = sum(sentiments) / len(sentiments)
        variance = sum((s - mean) ** 2 for s in sentiments) / len(sentiments)
        return variance ** 0.5
    
    def _generate_actionable_insights(self, weekly_metrics: Dict[str, Any], 
                                     daily_stats: List[DailyStats], db: Session) -> Dict[str, str]:
        """Generate actionable insights and recommendations"""
        
        # Analyze positive and negative patterns
        positive_topics = []
        negative_topics = []
        recommendations = []
        
        # Sentiment-based recommendations
        if weekly_metrics['overall_sentiment'] < settings.burnout_threshold:
            recommendations.append("Team sentiment is concerning. Consider scheduling 1:1s to check in with team members.")
            recommendations.append("Review current workload and deadlines to identify potential stress factors.")
        
        if weekly_metrics['sentiment_trend'] == "declining":
            recommendations.append("Sentiment is declining. Investigate recent changes or challenges affecting the team.")
            positive_topics.append("Early intervention needed")
        
        if weekly_metrics['engagement_level'] == "low":
            recommendations.append("Low engagement detected. Consider team building activities or process improvements.")
            recommendations.append("Review communication channels and ensure team members feel heard.")
        
        # Burnout-specific recommendations
        if weekly_metrics['burnout_warning']:
            recommendations.append("Burnout risk detected. Prioritize workload balancing and support for at-risk team members.")
            recommendations.append("Consider implementing wellness initiatives and mental health resources.")
            negative_topics.append("Burnout risk identified")
        
        # Positive reinforcement
        if weekly_metrics['overall_sentiment'] > 0.3:
            positive_topics.append("Strong positive team sentiment")
            recommendations.append("Great team morale! Continue current practices and recognize team achievements.")
        
        if weekly_metrics['engagement_level'] == "high":
            positive_topics.append("High team engagement levels")
            recommendations.append("Excellent engagement! Consider documenting successful practices for consistency.")
        
        # Channel-specific insights
        channel_insights = self._analyze_channel_patterns(daily_stats)
        recommendations.extend(channel_insights)
        
        return {
            'top_positive_topics': json.dumps(positive_topics),
            'top_negative_topics': json.dumps(negative_topics),
            'recommendations': json.dumps(recommendations)
        }
    
    def _analyze_channel_patterns(self, daily_stats: List[DailyStats]) -> List[str]:
        """Analyze patterns across different channels"""
        recommendations = []
        
        # Group by channel
        channel_stats = {}
        for stat in daily_stats:
            if stat.channel_id not in channel_stats:
                channel_stats[stat.channel_id] = []
            channel_stats[stat.channel_id].append(stat)
        
        # Analyze each channel
        for channel_id, stats in channel_stats.items():
            avg_sentiment = sum(s.avg_sentiment for s in stats if s.avg_sentiment is not None) / len(stats)
            avg_engagement = sum(s.response_rate for s in stats) / len(stats)
            
            if avg_sentiment < -0.3:
                recommendations.append(f"Channel {channel_id[:8]}... shows consistently low sentiment. Review recent discussions.")
            
            if avg_engagement < 0.2:
                recommendations.append(f"Channel {channel_id[:8]}... has low engagement. Consider improving communication.")
        
        return recommendations
    
    def get_dashboard_data(self, days: int = 7) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for the specified number of days
        
        Args:
            days: Number of days to include in the analysis
            
        Returns:
            Dictionary containing dashboard data
        """
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        db = next(get_db())
        try:
            # Get daily stats for the period
            daily_stats = db.query(DailyStats).filter(
                and_(
                    func.date(DailyStats.date) >= start_date,
                    func.date(DailyStats.date) <= end_date
                )
            ).all()
            
            # Get latest team insight
            latest_insight = db.query(TeamInsight).order_by(TeamInsight.week_start.desc()).first()
            
            # Get monitored channels
            channels = db.query(MonitoredChannel).filter(MonitoredChannel.is_active == True).all()
            
            # Prepare dashboard data
            dashboard_data = {
                'summary': self._prepare_summary_data(daily_stats),
                'trends': self._prepare_trend_data(daily_stats),
                'channels': self._prepare_channel_data(daily_stats, channels),
                'insights': self._prepare_insights_data(latest_insight),
                'burnout_alerts': self._prepare_burnout_alerts(latest_insight),
                'recommendations': self._prepare_recommendations(latest_insight)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}
        finally:
            db.close()
    
    def _prepare_summary_data(self, daily_stats: List[DailyStats]) -> Dict[str, Any]:
        """Prepare summary metrics for dashboard"""
        if not daily_stats:
            return {}
        
        total_messages = sum(stat.message_count for stat in daily_stats)
        total_users = len(set(stat.channel_id + str(stat.unique_users) for stat in daily_stats))
        
        all_sentiments = [stat.avg_sentiment for stat in daily_stats if stat.avg_sentiment is not None]
        avg_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0.0
        
        avg_engagement = sum(stat.response_rate for stat in daily_stats) / len(daily_stats)
        
        return {
            'total_messages': total_messages,
            'active_users': total_users,
            'avg_sentiment': round(avg_sentiment, 3),
            'avg_engagement': round(avg_engagement, 3),
            'sentiment_category': self.sentiment_service.categorize_sentiment(avg_sentiment)
        }
    
    def _prepare_trend_data(self, daily_stats: List[DailyStats]) -> List[Dict[str, Any]]:
        """Prepare trend data for charts"""
        # Group by date and calculate daily aggregates
        date_stats = {}
        for stat in daily_stats:
            date_key = stat.date.date()
            if date_key not in date_stats:
                date_stats[date_key] = {
                    'date': date_key.isoformat(),
                    'sentiments': [],
                    'messages': 0,
                    'engagement': []
                }
            
            date_stats[date_key]['sentiments'].append(stat.avg_sentiment)
            date_stats[date_key]['messages'] += stat.message_count
            date_stats[date_key]['engagement'].append(stat.response_rate)
        
        # Calculate daily averages
        trend_data = []
        for date_key in sorted(date_stats.keys()):
            stats = date_stats[date_key]
            sentiments = [s for s in stats['sentiments'] if s is not None]
            
            trend_data.append({
                'date': stats['date'],
                'sentiment': round(sum(sentiments) / len(sentiments), 3) if sentiments else 0.0,
                'messages': stats['messages'],
                'engagement': round(sum(stats['engagement']) / len(stats['engagement']), 3)
            })
        
        return trend_data
    
    def _prepare_channel_data(self, daily_stats: List[DailyStats], 
                             channels: List[MonitoredChannel]) -> List[Dict[str, Any]]:
        """Prepare channel-specific data"""
        channel_data = []
        
        # Group stats by channel
        channel_stats = {}
        for stat in daily_stats:
            if stat.channel_id not in channel_stats:
                channel_stats[stat.channel_id] = []
            channel_stats[stat.channel_id].append(stat)
        
        # Get channel info
        channel_info = {ch.channel_id: ch for ch in channels}
        
        for channel_id, stats in channel_stats.items():
            if channel_id in channel_info:
                sentiments = [s.avg_sentiment for s in stats if s.avg_sentiment is not None]
                avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
                
                total_messages = sum(s.message_count for s in stats)
                avg_engagement = sum(s.response_rate for s in stats) / len(stats)
                
                channel_data.append({
                    'channel_id': channel_id,
                    'channel_name': channel_info[channel_id].channel_name,
                    'avg_sentiment': round(avg_sentiment, 3),
                    'total_messages': total_messages,
                    'avg_engagement': round(avg_engagement, 3),
                    'sentiment_category': self.sentiment_service.categorize_sentiment(avg_sentiment)
                })
        
        return sorted(channel_data, key=lambda x: x['total_messages'], reverse=True)
    
    def _prepare_insights_data(self, team_insight: Optional[TeamInsight]) -> Dict[str, Any]:
        """Prepare team insights data"""
        if not team_insight:
            return {}
        
        return {
            'overall_sentiment': round(team_insight.overall_sentiment, 3),
            'sentiment_trend': team_insight.sentiment_trend,
            'engagement_level': team_insight.engagement_level,
            'burnout_risk_score': round(team_insight.burnout_risk_score, 3),
            'week_start': team_insight.week_start.isoformat(),
            'week_end': team_insight.week_end.isoformat()
        }
    
    def _prepare_burnout_alerts(self, team_insight: Optional[TeamInsight]) -> List[Dict[str, Any]]:
        """Prepare burnout alerts"""
        if not team_insight or not team_insight.burnout_warning:
            return []
        
        alerts = []
        
        if team_insight.at_risk_users:
            at_risk_users = json.loads(team_insight.at_risk_users)
            for user_data in at_risk_users:
                alerts.append({
                    'type': 'burnout_risk',
                    'severity': 'high' if user_data['risk_score'] > 0.7 else 'medium',
                    'message': f"User {user_data['user_id'][:8]}... shows burnout risk (score: {user_data['risk_score']:.2f})",
                    'user_id': user_data['user_id']
                })
        
        if team_insight.overall_sentiment < settings.burnout_threshold:
            alerts.append({
                'type': 'low_sentiment',
                'severity': 'high',
                'message': f"Team sentiment is very low ({team_insight.overall_sentiment:.2f})"
            })
        
        return alerts
    
    def _prepare_recommendations(self, team_insight: Optional[TeamInsight]) -> List[str]:
        """Prepare actionable recommendations"""
        if not team_insight or not team_insight.recommendations:
            return []
        
        try:
            return json.loads(team_insight.recommendations)
        except (json.JSONDecodeError, TypeError):
            return []
