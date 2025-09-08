"""
Base models và schemas chung
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model cho tất cả API responses"""
    success: bool = True
    message: str = "OK"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[dict] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    mongodb: str
    redis: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
