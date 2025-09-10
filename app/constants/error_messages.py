"""
Error messages mappings for FX API
"""

from .error_codes import ErrorCodes

ERROR_MESSAGES = {
    # Success
    ErrorCodes.SUCCESS: "Success",
    
    # AI API errors
    ErrorCodes.AI_API_TIMEOUT: "AI API timeout after 30 seconds",
    ErrorCodes.AI_API_ERROR: "AI API returned error: {details}",
    ErrorCodes.AI_API_INVALID_RESPONSE: "AI API returned invalid response format",
    ErrorCodes.AI_API_RATE_LIMIT: "AI API rate limit exceeded",
    
    # Redis errors
    ErrorCodes.REDIS_CONNECTION_ERROR: "Redis connection failed",
    ErrorCodes.REDIS_LOCK_TIMEOUT: "Redis lock timeout after 2 minutes",
    ErrorCodes.REDIS_CACHE_ERROR: "Redis cache operation failed: {details}",
    ErrorCodes.REDIS_LOCK_ACQUISITION_FAILED: "Failed to acquire Redis lock",
    
    # Validation errors
    ErrorCodes.INVALID_INPUT: "Invalid input data",
    ErrorCodes.MISSING_REQUIRED_FIELD: "Missing required field: {field}",
    ErrorCodes.INVALID_CACHE_KEY: "Invalid cache key format",
    ErrorCodes.INVALID_SYMBOL: "Invalid symbol: {symbol}",
    ErrorCodes.INVALID_TIMEFRAME: "Invalid timeframe: {timeframe}",
    ErrorCodes.INVALID_TIMEZONE: "Invalid timezone: {timezone}",
    
    # Service errors
    ErrorCodes.SIGNAL_SERVICE_ERROR: "Signal service error: {details}",
    ErrorCodes.RISK_MANAGER_SERVICE_ERROR: "Risk manager service error: {details}",
    ErrorCodes.PROMPT_SERVICE_ERROR: "Prompt service error: {details}",
    
    # System errors
    ErrorCodes.INTERNAL_SERVER_ERROR: "Internal server error",
    ErrorCodes.SERVICE_UNAVAILABLE: "Service temporarily unavailable",
    ErrorCodes.DATABASE_ERROR: "Database operation failed",
    
    # Cache errors
    ErrorCodes.CACHE_MISS: "Cache miss for key: {key}",
    ErrorCodes.CACHE_WRITE_ERROR: "Failed to write to cache: {details}",
    ErrorCodes.CACHE_READ_ERROR: "Failed to read from cache: {details}",
}
