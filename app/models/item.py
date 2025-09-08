"""
Item models cho các API versions
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseResponse

# Common base item
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)

# V1 Models (Simple)
class ItemCreateV1(ItemBase):
    """V1: Simple item creation"""
    pass

class ItemResponseV1(BaseResponse):
    """V1: Simple item response"""
    data: dict

class ItemV1(ItemBase):
    """V1: Item representation"""
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# V2 Models (Enhanced)
class ItemCreateV2(ItemBase):
    """V2: Enhanced item creation với tags và metadata"""
    tags: Optional[list[str]] = Field(default=[], max_items=10)
    metadata: Optional[dict] = Field(default={})
    category: Optional[str] = Field(default="general", max_length=50)
    priority: Optional[int] = Field(default=1, ge=1, le=5)

class ItemResponseV2(BaseResponse):
    """V2: Enhanced response với pagination info"""
    data: dict
    meta: Optional[dict] = None

class ItemV2(ItemBase):
    """V2: Enhanced item representation"""
    id: str
    tags: list[str] = []
    metadata: dict = {}
    category: str = "general"
    priority: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    version: int = 2

class ItemUpdateV2(BaseModel):
    """V2: Item update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    tags: Optional[list[str]] = Field(None, max_items=10)
    metadata: Optional[dict] = None
    category: Optional[str] = Field(None, max_length=50)
    priority: Optional[int] = Field(None, ge=1, le=5)

class ItemListResponseV2(BaseResponse):
    """V2: Paginated list response"""
    data: list[ItemV2]
    meta: dict = Field(default_factory=lambda: {
        "total": 0,
        "page": 1,
        "per_page": 10,
        "pages": 0
    })
