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
    
    # Timeout configurations - Centralized management
    # Nginx timeout settings
    NGINX_PROXY_CONNECT_TIMEOUT: int = int(os.getenv("NGINX_PROXY_CONNECT_TIMEOUT", "300"))  # 5 minutes
    NGINX_PROXY_SEND_TIMEOUT: int = int(os.getenv("NGINX_PROXY_SEND_TIMEOUT", "300"))  # 5 minutes
    NGINX_PROXY_READ_TIMEOUT: int = int(os.getenv("NGINX_PROXY_READ_TIMEOUT", "300"))  # 5 minutes
    
    # AI Provider timeout settings
    AI_PROVIDER_TIMEOUT: int = int(os.getenv("AI_PROVIDER_TIMEOUT", "300"))  # 5 minutes
    AI_PROVIDER_RETRY_ATTEMPTS: int = int(os.getenv("AI_PROVIDER_RETRY_ATTEMPTS", "3"))
    AI_PROVIDER_RETRY_MIN_WAIT: int = int(os.getenv("AI_PROVIDER_RETRY_MIN_WAIT", "2"))
    AI_PROVIDER_RETRY_MAX_WAIT: int = int(os.getenv("AI_PROVIDER_RETRY_MAX_WAIT", "10"))
    
    # Redis timeout settings
    REDIS_LOCK_TIMEOUT: int = int(os.getenv("REDIS_LOCK_TIMEOUT", "300"))  # 5 minutes
    REDIS_CACHE_WAIT_TIMEOUT: int = int(os.getenv("REDIS_CACHE_WAIT_TIMEOUT", "300"))  # 5 minutes
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "600"))  # 10 minutes
    REDIS_BLOCKING_TIMEOUT: float = float(os.getenv("REDIS_BLOCKING_TIMEOUT", "0.1"))  # 100ms
    
    # Signal Service timeout settings
    SIGNAL_SERVICE_LOCK_TIMEOUT: int = int(os.getenv("SIGNAL_SERVICE_LOCK_TIMEOUT", "300"))  # 5 minutes
    SIGNAL_SERVICE_CACHE_WAIT_TIMEOUT: int = int(os.getenv("SIGNAL_SERVICE_CACHE_WAIT_TIMEOUT", "300"))  # 5 minutes
    SIGNAL_SERVICE_CACHE_TTL: int = int(os.getenv("SIGNAL_SERVICE_CACHE_TTL", "600"))  # 10 minutes

settings = Settings()
