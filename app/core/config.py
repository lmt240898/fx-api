"""
Core configuration settings
"""
import os
from typing import Optional

class Settings:
    # Database settings
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    MONGO_DATABASE: str = os.getenv("MONGO_DATABASE", "fx_api_db")
    
    # Redis settings
    REDIS_URI: str = os.getenv("REDIS_URI", "redis://redis:6379")
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    
    # App metadata
    APP_NAME: str = "FX API"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Multi-version FastAPI application with MongoDB and Redis"
    
    # Security
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()
