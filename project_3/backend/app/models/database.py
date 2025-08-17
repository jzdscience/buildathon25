from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
from ..config import settings

# Create database engine
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class MonitoredChannel(Base):
    __tablename__ = "monitored_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, unique=True, index=True)
    channel_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="channel", cascade="all, delete-orphan")
    daily_stats = relationship("DailyStats", back_populates="channel", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    channel_id = Column(String, ForeignKey("monitored_channels.channel_id"))
    user_id = Column(String, index=True)
    text = Column(Text)
    timestamp = Column(DateTime)
    
    # Sentiment scores
    text_sentiment = Column(Float)  # -1 to 1
    emoji_sentiment = Column(Float)  # -1 to 1
    overall_sentiment = Column(Float)  # Combined score
    
    # Metadata
    has_thread = Column(Boolean, default=False)
    reaction_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    channel = relationship("MonitoredChannel", back_populates="messages")
    reactions = relationship("Reaction", back_populates="message", cascade="all, delete-orphan")


class Reaction(Base):
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, ForeignKey("messages.message_id"))
    emoji = Column(String)
    count = Column(Integer, default=1)
    sentiment_score = Column(Float)  # Emoji sentiment score
    
    # Relationships
    message = relationship("Message", back_populates="reactions")


class DailyStats(Base):
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, ForeignKey("monitored_channels.channel_id"))
    date = Column(DateTime, index=True)
    
    # Aggregated metrics
    message_count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    avg_sentiment = Column(Float)
    min_sentiment = Column(Float)
    max_sentiment = Column(Float)
    
    # Sentiment distribution
    positive_count = Column(Integer, default=0)  # > 0.1
    neutral_count = Column(Integer, default=0)   # -0.1 to 0.1
    negative_count = Column(Integer, default=0)  # < -0.1
    
    # Engagement metrics
    total_reactions = Column(Integer, default=0)
    thread_count = Column(Integer, default=0)
    response_rate = Column(Float)  # % of messages with replies/reactions
    
    # Relationships
    channel = relationship("MonitoredChannel", back_populates="daily_stats")


class TeamInsight(Base):
    __tablename__ = "team_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(DateTime, index=True)
    week_end = Column(DateTime)
    
    # Weekly metrics
    overall_sentiment = Column(Float)
    sentiment_trend = Column(String)  # "improving", "declining", "stable"
    engagement_level = Column(String)  # "high", "medium", "low"
    
    # Burnout indicators
    burnout_risk_score = Column(Float)  # 0 to 1
    burnout_warning = Column(Boolean, default=False)
    at_risk_users = Column(Text)  # JSON list of user IDs
    
    # Key insights
    top_positive_topics = Column(Text)  # JSON list
    top_negative_topics = Column(Text)  # JSON list
    recommendations = Column(Text)  # JSON list of actionable recommendations
    
    created_at = Column(DateTime, default=datetime.utcnow)


class UserMetrics(Base):
    __tablename__ = "user_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    week_start = Column(DateTime, index=True)
    
    # User-specific metrics
    message_count = Column(Integer, default=0)
    avg_sentiment = Column(Float)
    sentiment_volatility = Column(Float)  # Standard deviation of sentiment
    
    # Engagement patterns
    active_days = Column(Integer, default=0)
    avg_response_time = Column(Float)  # In minutes
    interaction_count = Column(Integer, default=0)
    
    # Risk indicators
    consecutive_negative_days = Column(Integer, default=0)
    burnout_risk = Column(Float)  # 0 to 1


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

