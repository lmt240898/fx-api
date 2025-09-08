"""
API V1 - Health check endpoints
"""
from fastapi import APIRouter
from ...models.base import HealthResponse
from ...core.database import db_manager
from ...core.config import settings

router = APIRouter(tags=["Health V1"])

@router.get("/health", response_model=HealthResponse)
async def health_check_v1():
    """V1: Health check endpoint"""
    db_status = await db_manager.get_health_status()
    
    return HealthResponse(
        status="healthy",
        version=f"{settings.APP_VERSION} (API v1)",
        mongodb=db_status["mongodb"],
        redis=db_status["redis"]
    )
