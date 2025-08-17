from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models.database import get_db, MonitoredChannel
from ..services import SlackService, AnalyticsService
from ..config import settings

# API Models
class ChannelAdd(BaseModel):
    channel_id: str

class ChannelResponse(BaseModel):
    channel_id: str
    channel_name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    summary: Dict[str, Any]
    trends: List[Dict[str, Any]]
    channels: List[Dict[str, Any]]
    insights: Dict[str, Any]
    burnout_alerts: List[Dict[str, Any]]
    recommendations: List[str]

class SlackConnectionTest(BaseModel):
    success: bool
    user: Optional[str] = None
    team: Optional[str] = None
    error: Optional[str] = None

# Initialize services
slack_service = SlackService()
analytics_service = AnalyticsService()

# Create router
api_router = APIRouter()

# Health check
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Slack connection test
@api_router.get("/slack/test", response_model=SlackConnectionTest)
async def test_slack_connection():
    """Test Slack API connection"""
    try:
        result = await slack_service.test_connection()
        return SlackConnectionTest(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test Slack connection: {str(e)}")

# Channel management
@api_router.get("/channels", response_model=List[ChannelResponse])
async def get_monitored_channels(db: Session = Depends(get_db)):
    """Get list of monitored channels"""
    try:
        channels = await slack_service.get_monitored_channels(db)
        return [ChannelResponse.model_validate(channel) for channel in channels]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get channels: {str(e)}")

@api_router.post("/channels", response_model=ChannelResponse)
async def add_channel(
    channel_data: ChannelAdd, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Add a new channel to monitor"""
    try:
        channel = await slack_service.add_channel(channel_data.channel_id, db)
        
        # Start background sync for this channel
        background_tasks.add_task(slack_service.sync_channel_messages, channel_data.channel_id, db)
        
        return ChannelResponse.model_validate(channel)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add channel: {str(e)}")

@api_router.delete("/channels/{channel_id}")
async def remove_channel(channel_id: str, db: Session = Depends(get_db)):
    """Remove a channel from monitoring"""
    try:
        success = await slack_service.remove_channel(channel_id, db)
        if success:
            return {"message": "Channel removed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Channel not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to remove channel: {str(e)}")

# Dashboard data
@api_router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(days: int = 7):
    """Get dashboard data for the specified number of days"""
    try:
        if days < 1 or days > 30:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 30")
        
        dashboard_data = analytics_service.get_dashboard_data(days=days)
        return DashboardResponse(**dashboard_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

# Analytics endpoints
@api_router.post("/analytics/daily-stats")
async def generate_daily_stats(
    background_tasks: BackgroundTasks,
    target_date: Optional[str] = None
):
    """Generate daily statistics"""
    try:
        parsed_date = None
        if target_date:
            try:
                parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        background_tasks.add_task(analytics_service.generate_daily_stats, parsed_date)
        return {"message": "Daily stats generation started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate daily stats: {str(e)}")

@api_router.post("/analytics/weekly-insights")
async def generate_weekly_insights(
    background_tasks: BackgroundTasks,
    week_start: Optional[str] = None
):
    """Generate weekly team insights"""
    try:
        parsed_date = None
        if week_start:
            try:
                parsed_date = datetime.strptime(week_start, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        background_tasks.add_task(analytics_service.generate_weekly_insights, parsed_date)
        return {"message": "Weekly insights generation started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate weekly insights: {str(e)}")

# Sentiment analysis
@api_router.get("/sentiment/trends")
async def get_sentiment_trends(days: int = 7, channel_id: Optional[str] = None):
    """Get sentiment trends over time"""
    try:
        if days < 1 or days > 30:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 30")
        
        # This would be implemented to return detailed sentiment trends
        # For now, returning a placeholder
        return {"message": "Sentiment trends endpoint - implementation pending", "days": days, "channel_id": channel_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sentiment trends: {str(e)}")

# Monitoring controls
@api_router.post("/monitoring/start")
async def start_monitoring():
    """Start Slack monitoring"""
    try:
        await slack_service.start_monitoring()
        return {"message": "Slack monitoring started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@api_router.post("/monitoring/stop")
async def stop_monitoring():
    """Stop Slack monitoring"""
    try:
        await slack_service.stop_monitoring()
        return {"message": "Slack monitoring stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")

@api_router.get("/monitoring/status")
async def get_monitoring_status():
    """Get monitoring status"""
    try:
        is_monitoring = slack_service.is_monitoring
        return {
            "is_monitoring": is_monitoring,
            "status": "active" if is_monitoring else "stopped",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring status: {str(e)}")

# Configuration
@api_router.get("/config")
async def get_configuration():
    """Get current configuration"""
    return {
        "sentiment_update_interval_minutes": settings.sentiment_update_interval_minutes,
        "burnout_threshold": settings.burnout_threshold,
        "warning_threshold": settings.warning_threshold,
        "api_host": settings.api_host,
        "api_port": settings.api_port
    }

# Bulk operations
@api_router.post("/bulk/sync-channels")
async def sync_all_channels(background_tasks: BackgroundTasks):
    """Trigger sync for all monitored channels"""
    try:
        background_tasks.add_task(slack_service.sync_all_channels)
        return {"message": "Channel sync started for all monitored channels"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync channels: {str(e)}")

@api_router.post("/bulk/generate-analytics")
async def generate_all_analytics(background_tasks: BackgroundTasks):
    """Generate all analytics (daily stats and weekly insights)"""
    try:
        # Generate daily stats for yesterday
        yesterday = (datetime.utcnow() - timedelta(days=1)).date()
        background_tasks.add_task(analytics_service.generate_daily_stats, yesterday)
        
        # Generate weekly insights for last week
        today = datetime.utcnow().date()
        last_monday = today - timedelta(days=today.weekday() + 7)
        background_tasks.add_task(analytics_service.generate_weekly_insights, last_monday)
        
        return {"message": "Analytics generation started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")

# Statistics
@api_router.get("/stats/summary")
async def get_stats_summary(db: Session = Depends(get_db)):
    """Get summary statistics"""
    try:
        # Get basic counts
        channels_count = db.query(MonitoredChannel).filter(MonitoredChannel.is_active == True).count()
        
        return {
            "monitored_channels": channels_count,
            "monitoring_active": slack_service.is_monitoring,
            "last_updated": datetime.utcnow(),
            "system_status": "operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats summary: {str(e)}")

# Export endpoints
@api_router.get("/export/dashboard-data")
async def export_dashboard_data(days: int = 7, format: str = "json"):
    """Export dashboard data"""
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
        
        dashboard_data = analytics_service.get_dashboard_data(days=days)
        
        # For now, always return JSON. CSV export would require additional processing
        return {
            "data": dashboard_data,
            "export_date": datetime.utcnow(),
            "days_included": days,
            "format": format
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")
