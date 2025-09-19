from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.signal_service import SignalService
from app.services.risk_manager_service import RiskManagerService
from app.services.tracking_service import TrackingService
from app.utils.response_handler import ResponseHandler
from app.utils.logger import Logger

router = APIRouter()
logger = Logger("trading_api")

# Request models
class SignalRequest(BaseModel):
    cache_key: Dict[str, str]
    symbol: str
    timeframe: str
    account_info: Dict[str, Any]
    balance_config: Dict[str, Any]
    max_positions: int
    active_orders_summary: str
    pending_orders_summary: str
    portfolio_exposure: Dict[str, Any]
    account_type_details: Dict[str, Any]
    symbol_info: Dict[str, Any]
    multi_timeframes: Dict[str, Any]

class RiskManagerRequest(BaseModel):
    proposed_signal_json: Dict[str, Any]
    account_info_json: Dict[str, Any]
    symbol_info: Dict[str, Any]
    portfolio_exposure_json: Dict[str, Any]
    balance_config: Dict[str, Any]
    correlation_groups_json: Dict[str, Any]
    symbol: Dict[str, str]
    lot_size_to_margin_map: Dict[str, float]

class TrackingDataRequest(BaseModel):
    login: str
    ticket: str
    synthetic_params_signal: Dict[str, Any]
    synthetic_response_signal: Dict[str, Any]
    synthetic_params_risk_manager: Dict[str, Any]
    synthetic_response_risk_manager: Dict[str, Any]

# Initialize services
signal_service = SignalService()
risk_manager_service = RiskManagerService()
tracking_service = TrackingService()

@router.post("/signal")
async def get_signal(request: SignalRequest):
    """
    Signal analysis endpoint with caching and distributed locking
    
    Args:
        request: Signal request data
        
    Returns:
        Signal analysis result
    """
    try:
        logger.info(f"Signal request received for {request.symbol} {request.timeframe}")
        
        # Convert Pydantic model to dict
        request_data = request.dict()
        
        # Process signal with caching
        result = await signal_service.analyze_signal(request_data)
        
        logger.info(f"Signal request completed for {request.symbol} {request.timeframe}")
        return result
        
    except Exception as e:
        logger.error(f"Signal endpoint error: {str(e)}")
        return ResponseHandler.internal_server_error()

@router.post("/risk_manager")
async def get_risk_manager(request: RiskManagerRequest):
    """
    Risk manager endpoint
    
    Args:
        request: Risk manager request data
        
    Returns:
        Risk management result
    """
    try:
        logger.info(f"Risk manager request received for {request.symbol.get('origin_name', 'unknown')}")
        
        # Convert Pydantic model to dict
        request_data = request.dict()
        
        # Process risk management
        result = risk_manager_service.analyze_risk(request_data)
        
        logger.info(f"Risk manager request completed for {request.symbol.get('origin_name', 'unknown')}")
        return ResponseHandler.success(result)
        
    except Exception as e:
        logger.error(f"Risk manager endpoint error: {str(e)}")
        return ResponseHandler.internal_server_error()

@router.post("/tracking_data")
async def save_tracking_data(request: TrackingDataRequest):
    """
    Tracking data endpoint - saves tracking data for audit and analysis
    
    Args:
        request: Tracking data request containing login, ticket, and synthetic params
        
    Returns:
        Tracking data save result
    """
    try:
        logger.info(f"Tracking data request received for login: {request.login}, ticket: {request.ticket}")
        
        # Convert Pydantic model to dict
        request_data = request.dict()
        
        # Process tracking data
        result = tracking_service.save_tracking_data(request_data)
        
        logger.info(f"Tracking data request completed for login: {request.login}, ticket: {request.ticket}")
        return result
        
    except Exception as e:
        logger.error(f"Tracking data endpoint error: {str(e)}")
        return ResponseHandler.internal_server_error()
