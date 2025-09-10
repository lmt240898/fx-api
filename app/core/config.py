"""
Core configuration settings
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Database settings - Auto-detect environment
    def _get_mongo_uri():
        if os.getenv("MONGO_URI"):
            return os.getenv("MONGO_URI")
        # Check if running in Docker (container name exists)
        try:
            import socket
            socket.gethostbyname("mongo")
            return "mongodb://mongo:27017"  # Docker environment
        except:
            return "mongodb://localhost:9917"  # Local development
    
    def _get_redis_uri():
        if os.getenv("REDIS_URI"):
            return os.getenv("REDIS_URI")
        # Check if running in Docker (container name exists)
        try:
            import socket
            socket.gethostbyname("redis")
            return "redis://redis:6379"  # Docker environment
        except:
            return "redis://localhost:9979"  # Local development
    
    MONGO_URI: str = _get_mongo_uri()
    MONGO_DATABASE: str = os.getenv("MONGO_DATABASE", "fx_api_db")
    
    # Redis settings
    REDIS_URI: str = _get_redis_uri()
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    
    # App metadata
    APP_NAME: str = "FX API"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Multi-version FastAPI application with MongoDB and Redis"
    
    # 3rd Party API settings
    AI_API_KEY: Optional[str] = os.getenv("AI_API_KEY")
    AI_API_ENDPOINT: str = os.getenv("AI_API_ENDPOINT", "https://openrouter.ai/api/v1")

    # Security
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()
