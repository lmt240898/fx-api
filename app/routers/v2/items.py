"""
API V2 - Enhanced Items endpoints
Với features mới: tags, metadata, pagination, filtering
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from ...models.item import (
    ItemCreateV2, ItemResponseV2, ItemUpdateV2, 
    ItemListResponseV2, ItemV2
)
from ...services.item_service import item_service
from ...services.redis_service import redis_service

router = APIRouter(prefix="/items", tags=["Items V2"])

@router.post("/", response_model=ItemResponseV2, status_code=status.HTTP_201_CREATED)
async def create_item_v2(item: ItemCreateV2):
    """
    V2: Tạo item mới với enhanced features
    - Tags support
    - Metadata support  
    - Category và priority
    - Enhanced response format
    """
    try:
        result = await item_service.create_item_v2(item)
        
        # Cache the created item
        cache_key = f"item_v2:{result['id']}"
        await redis_service.set_cache(cache_key, result, ttl=3600)
        
        return ItemResponseV2(
            message="Item created successfully",
            data=result,
            meta={"version": 2, "cached": True}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create item: {str(e)}"
        )

@router.get("/{item_id}", response_model=ItemResponseV2)
async def get_item_v2(item_id: str):
    """
    V2: Lấy item theo ID với caching
    - Enhanced response format
    - Redis caching
    - Full item data với metadata
    """
    # Try cache first
    cache_key = f"item_v2:{item_id}"
    cached_item = await redis_service.get_cache(cache_key)
    
    if cached_item:
        return ItemResponseV2(
            message="Item retrieved from cache",
            data=cached_item,
            meta={"cached": True, "version": 2}
        )
    
    # Get from database
    item = await item_service.get_item_v2(item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    item_dict = item.dict()
    
    # Cache for next time
    await redis_service.set_cache(cache_key, item_dict, ttl=3600)
    
    return ItemResponseV2(
        message="Item retrieved successfully",
        data=item_dict,
        meta={"cached": False, "version": 2}
    )

@router.put("/{item_id}", response_model=ItemResponseV2)
async def update_item_v2(item_id: str, item_update: ItemUpdateV2):
    """
    V2: Cập nhật item
    - Partial updates supported
    - Cache invalidation
    """
    try:
        updated_item = await item_service.update_item_v2(item_id, item_update)
        
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found or no changes made"
            )
        
        # Invalidate cache
        cache_key = f"item_v2:{item_id}"
        await redis_service.delete_cache(cache_key)
        
        return ItemResponseV2(
            message="Item updated successfully",
            data=updated_item.dict(),
            meta={"version": 2, "cache_invalidated": True}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update item: {str(e)}"
        )

@router.delete("/{item_id}", response_model=ItemResponseV2)
async def delete_item_v2(item_id: str):
    """
    V2: Xóa item
    - Cache invalidation
    """
    try:
        success = await item_service.delete_item_v2(item_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Invalidate cache
        cache_key = f"item_v2:{item_id}"
        await redis_service.delete_cache(cache_key)
        
        return ItemResponseV2(
            message="Item deleted successfully",
            data={"deleted_id": item_id},
            meta={"version": 2, "cache_invalidated": True}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete item: {str(e)}"
        )

@router.get("/", response_model=ItemListResponseV2)
async def list_items_v2(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags")
):
    """
    V2: List items với pagination và filtering
    - Pagination support
    - Category filtering
    - Tags filtering
    - Caching support
    """
    try:
        # Create cache key based on parameters
        cache_key = f"items_v2:page_{page}:per_page_{per_page}:cat_{category}:tags_{','.join(tags or [])}"
        
        # Try cache first
        cached_result = await redis_service.get_cache(cache_key)
        if cached_result:
            return ItemListResponseV2(
                message="Items retrieved from cache",
                data=[ItemV2(**item) for item in cached_result["items"]],
                meta={**cached_result["meta"], "cached": True, "version": 2}
            )
        
        # Get from database
        result = await item_service.list_items_v2(page, per_page, category, tags)
        
        # Prepare response
        items_data = [item.dict() for item in result["items"]]
        
        # Cache result
        cache_data = {
            "items": items_data,
            "meta": result["meta"]
        }
        await redis_service.set_cache(cache_key, cache_data, ttl=300)  # 5 minutes
        
        return ItemListResponseV2(
            message="Items retrieved successfully",
            data=result["items"],
            meta={**result["meta"], "cached": False, "version": 2}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list items: {str(e)}"
        )
