"""
Common response handler for FX API
"""

from typing import Dict, Any, Optional
from app.constants import ErrorCodes, ERROR_MESSAGES


class ResponseHandler:
    """Standard response handler for all APIs"""
    
    @staticmethod
    def success(data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Create success response
        
        Args:
            data: Response data
            **kwargs: Additional fields (e.g., tracking_path_signal)
            
        Returns:
            Standard success response
        """
        response = {
            "success": True,
            "errorMsg": "",
            "errorCode": ErrorCodes.SUCCESS,
            "data": data
        }
        
        # Add additional fields if provided
        for key, value in kwargs.items():
            response[key] = value
            
        return response
    
    @staticmethod
    def error(error_code: int, **kwargs) -> Dict[str, Any]:
        """
        Create error response
        
        Args:
            error_code: Error code
            **kwargs: Additional parameters for error message formatting
            
        Returns:
            Standard error response
        """
        error_msg = ERROR_MESSAGES.get(error_code, "Unknown error")
        
        # Format message with kwargs if needed
        if kwargs:
            try:
                error_msg = error_msg.format(**kwargs)
            except (KeyError, ValueError):
                # If formatting fails, use original message
                pass
                
        return {
            "success": False,
            "errorMsg": error_msg,
            "errorCode": error_code,
            "data": {}
        }
    
    @staticmethod
    def ai_timeout() -> Dict[str, Any]:
        """AI API timeout error"""
        return ResponseHandler.error(ErrorCodes.AI_API_TIMEOUT)
    
    @staticmethod
    def ai_error(details: str) -> Dict[str, Any]:
        """AI API error with details"""
        return ResponseHandler.error(ErrorCodes.AI_API_ERROR, details=details)
    
    @staticmethod
    def redis_connection_error() -> Dict[str, Any]:
        """Redis connection error"""
        return ResponseHandler.error(ErrorCodes.REDIS_CONNECTION_ERROR)
    
    @staticmethod
    def redis_lock_timeout() -> Dict[str, Any]:
        """Redis lock timeout error"""
        return ResponseHandler.error(ErrorCodes.REDIS_LOCK_TIMEOUT)
    
    @staticmethod
    def validation_error(field: str) -> Dict[str, Any]:
        """Validation error for missing field"""
        return ResponseHandler.error(ErrorCodes.MISSING_REQUIRED_FIELD, field=field)
    
    @staticmethod
    def invalid_input() -> Dict[str, Any]:
        """Invalid input error"""
        return ResponseHandler.error(ErrorCodes.INVALID_INPUT)
    
    @staticmethod
    def signal_service_error(details: str) -> Dict[str, Any]:
        """Signal service error"""
        return ResponseHandler.error(ErrorCodes.SIGNAL_SERVICE_ERROR, details=details)
    
    @staticmethod
    def risk_manager_service_error(details: str) -> Dict[str, Any]:
        """Risk manager service error"""
        return ResponseHandler.error(ErrorCodes.RISK_MANAGER_SERVICE_ERROR, details=details)
    
    @staticmethod
    def internal_server_error() -> Dict[str, Any]:
        """Internal server error"""
        return ResponseHandler.error(ErrorCodes.INTERNAL_SERVER_ERROR)
