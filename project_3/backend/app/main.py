from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import asyncio
import os
from pathlib import Path
from datetime import datetime

from .config import settings
from .models.database import init_db
from .api.routes import api_router
from .services import SlackService, AnalyticsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global service instances
slack_service = SlackService()
analytics_service = AnalyticsService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Employee Engagement Pulse application...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Start background tasks
    try:
        # Start Slack monitoring if tokens are configured
        if settings.slack_bot_token and settings.slack_app_token:
            await slack_service.start_monitoring()
            logger.info("Slack monitoring started")
        else:
            logger.warning("Slack tokens not configured. Monitoring will not start automatically.")
        
        # Schedule periodic analytics generation
        asyncio.create_task(schedule_analytics_tasks())
        logger.info("Analytics tasks scheduled")
        
    except Exception as e:
        logger.error(f"Failed to start background services: {e}")
    
    logger.info("Application startup completed")
    
    yield
    
    # Cleanup
    logger.info("Shutting down application...")
    try:
        await slack_service.stop_monitoring()
        logger.info("Slack monitoring stopped")
    except Exception as e:
        logger.error(f"Error stopping Slack monitoring: {e}")
    
    logger.info("Application shutdown completed")

async def schedule_analytics_tasks():
    """Schedule periodic analytics tasks"""
    while True:
        try:
            # Wait for the configured interval
            await asyncio.sleep(settings.sentiment_update_interval_minutes * 60)
            
            # Generate daily stats
            analytics_service.generate_daily_stats()
            logger.info("Periodic daily stats generation completed")
            
            # Generate weekly insights if it's Monday
            from datetime import datetime
            if datetime.utcnow().weekday() == 0:  # Monday
                analytics_service.generate_weekly_insights()
                logger.info("Weekly insights generated")
                
        except Exception as e:
            logger.error(f"Error in scheduled analytics tasks: {e}")
            # Continue the loop even if there's an error
            await asyncio.sleep(60)  # Wait 1 minute before retrying

# Create FastAPI application
app = FastAPI(
    title="Employee Engagement Pulse",
    description="Monitor Slack channels and analyze team sentiment for actionable manager insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": str(datetime.utcnow())
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": str(datetime.utcnow())
        }
    )

# Include API router
app.include_router(api_router, prefix="/api/v1", tags=["api"])

# Serve static files if build directory exists (production mode)
# Try multiple possible locations for the frontend build
possible_static_dirs = [
    Path(__file__).parent.parent.parent / "frontend" / "build",  # Development structure
    Path(__file__).parent.parent / "frontend" / "build",  # Docker structure
    Path("/app/frontend/build"),  # Absolute path in Docker
]

static_dir = None
for possible_dir in possible_static_dirs:
    if possible_dir.exists() and possible_dir.is_dir():
        static_dir = possible_dir
        break

if static_dir:
    app.mount("/static", StaticFiles(directory=str(static_dir / "static")), name="static")
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="frontend")
    print(f"📁 Serving frontend build from {static_dir}")
else:
    # Development mode - API only
    print("🛠️  Development mode: Frontend not found, serving API only")
    
    # Root endpoint for development
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Employee Engagement Pulse API",
            "version": "1.0.0",
            "docs_url": "/docs",
            "status": "running",
            "monitoring_active": slack_service.is_monitoring,
            "mode": "development",
            "frontend_url": "http://localhost:3000"
        }

# Additional utility endpoints
@app.get("/status")
async def status():
    """Application status endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "slack_monitoring": slack_service.is_monitoring,
            "database": "connected",  # Could add actual DB health check
            "analytics": "active"
        },
        "configuration": {
            "update_interval_minutes": settings.sentiment_update_interval_minutes,
            "burnout_threshold": settings.burnout_threshold,
            "warning_threshold": settings.warning_threshold
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
