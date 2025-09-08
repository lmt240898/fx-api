from fastapi import APIRouter, Response

router = APIRouter()

@router.get("/signal")
async def get_signal():
    """Endpoint for signal (to be implemented)"""
    return Response(content="ok", media_type="text/plain")

@router.get("/risk_manager")
async def get_risk_manager():
    """Endpoint for risk manager (to be implemented)"""
    return Response(content="ok", media_type="text/plain")
