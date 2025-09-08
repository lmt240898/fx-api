"""
API V1 - Items endpoints (Simple CRUD)
Backward compatible với API hiện tại
"""
from fastapi import APIRouter, HTTPException, status
from ...models.item import ItemCreateV1, ItemResponseV1
from ...services.item_service import item_service

router = APIRouter(prefix="/items", tags=["Items V1"])

@router.post("/", response_model=ItemResponseV1, status_code=status.HTTP_201_CREATED)
async def create_item_v1(item: ItemCreateV1):
    """
    V1: Tạo item mới (simple)
    - Chỉ có name và description
    - Response đơn giản
    """
    try:
        result = await item_service.create_item_v1(item)
        return ItemResponseV1(
            message="Item created successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create item: {str(e)}"
        )

@router.get("/{item_id}", response_model=ItemResponseV1)
async def get_item_v1(item_id: str):
    """
    V1: Lấy item theo ID
    - Simple response format
    - Backward compatible
    """
    item = await item_service.get_item_v1(item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return ItemResponseV1(
        message="Item retrieved successfully",
        data=item
    )
