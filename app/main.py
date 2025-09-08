"""
Main FastAPI application với Multi-Version API support
Hỗ trợ API v1 (backward compatible) và v2 (enhanced features)
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Import core components
from .core.config import settings
from .core.database import db_manager

# Import routers
from .routers.v1 import items_router as v1_items, health_router as v1_health
from .routers.v2 import items_router as v2_items, health_router as v2_health

# Import services for testing
from .services.redis_service import redis_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await db_manager.connect_databases()
    yield
    # Shutdown  
    await db_manager.disconnect_databases()

# Tạo FastAPI app với lifespan management
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# API V1 Routes (Backward Compatible)
app.include_router(
    v1_items,
    prefix=settings.API_V1_PREFIX,
    tags=["API V1"]
)
app.include_router(
    v1_health,
    prefix=settings.API_V1_PREFIX,
    tags=["API V1"]
)

# API V2 Routes (Enhanced Features)
app.include_router(
    v2_items,
    prefix=settings.API_V2_PREFIX,
    tags=["API V2"]
)
app.include_router(
    v2_health,
    prefix=settings.API_V2_PREFIX,
    tags=["API V2"]
)

# Global health endpoint (no version prefix)
@app.get("/health")
async def global_health_check():
    """Global health check endpoint"""
    db_status = await db_manager.get_health_status()
    
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mongodb": db_status["mongodb"],
        "redis": db_status["redis"],
        "available_apis": {
            "v1": settings.API_V1_PREFIX,
            "v2": settings.API_V2_PREFIX
        }
    }

# Legacy Redis test endpoint (for backward compatibility)
@app.get("/redis/")
async def test_redis_legacy():
    """Legacy Redis test endpoint (backward compatibility)"""
    result = await redis_service.test_connection()
    return {
        "redis_value": result.get("test_result", "N/A"),
        "status": result["status"],
        "message": "Legacy endpoint - consider using API versioned endpoints"
    }

# Root endpoint với API documentation
@app.get("/")
async def root():
    """Root endpoint với API information"""
    return {
        "message": "Welcome to FX API",
        "version": settings.APP_VERSION,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "api_versions": {
            "v1": {
                "prefix": settings.API_V1_PREFIX,
                "description": "Simple CRUD operations - Backward compatible",
                "features": ["Basic CRUD", "Simple responses"]
            },
            "v2": {
                "prefix": settings.API_V2_PREFIX,
                "description": "Enhanced features with caching and advanced filtering",
                "features": [
                    "Enhanced CRUD", "Redis caching", "Pagination", 
                    "Filtering", "Tags support", "Metadata support"
                ]
            }
        }
    }
