from pydantic_settings import BaseSettings
from typing import List
from pydantic import Field


class Settings(BaseSettings):
    # Slack Configuration
    slack_bot_token: str = ""
    slack_app_token: str = ""
    
    # Database
    database_url: str = "sqlite:///./data/engagement_pulse.db"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # Sentiment Analysis
    sentiment_update_interval_minutes: int = 60
    burnout_threshold: float = -0.3
    warning_threshold: float = -0.5
    
    # Security
    secret_key: str = ""
    
    # Computed property for CORS origins list
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
