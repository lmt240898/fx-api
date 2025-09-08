"""
API V2 - Enhanced health check endpoints
"""
from fastapi import APIRouter
from ...models.base import HealthResponse
from ...core.database import db_manager
from ...core.config import settings
from ...services.redis_service import redis_service

router = APIRouter(tags=["Health V2"])

@router.get("/health", response_model=HealthResponse)
async def health_check_v2():
    """V2: Enhanced health check với detailed info"""
    db_status = await db_manager.get_health_status()
    
    return HealthResponse(
        status="healthy",
        version=f"{settings.APP_VERSION} (API v2)",
        mongodb=db_status["mongodb"],
        redis=db_status["redis"]
    )

@router.get("/health/detailed")
async def detailed_health_check_v2():
    """V2: Detailed health check với performance metrics"""
    import time
    start_time = time.time()
    
    # Test database connections
    db_status = await db_manager.get_health_status()
    redis_test = await redis_service.test_connection()
    
    response_time = round((time.time() - start_time) * 1000, 2)
    
    return {
        "status": "healthy",
        "version": f"{settings.APP_VERSION} (API v2)",
        "services": {
            "mongodb": {
                "status": db_status["mongodb"],
                "database": settings.MONGO_DATABASE
            },
            "redis": {
                "status": db_status["redis"],
                "test_result": redis_test
            }
        },
        "performance": {
            "response_time_ms": response_time
        },
        "config": {
            "debug_mode": settings.DEBUG,
            "api_v1_prefix": settings.API_V1_PREFIX,
            "api_v2_prefix": settings.API_V2_PREFIX
        }
    }
