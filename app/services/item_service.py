"""
Item service layer - Business logic cho items
"""
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from ..core.database import db_manager
from ..models.item import *

class ItemService:
    def __init__(self):
        self.collection_name = "items"
    
    @property
    def collection(self):
        return db_manager.db[self.collection_name]
    
    # V1 Methods (Simple CRUD)
    async def create_item_v1(self, item_data: ItemCreateV1) -> dict:
        """V1: Tạo item đơn giản"""
        item_dict = item_data.dict()
        item_dict["created_at"] = datetime.utcnow()
        item_dict["version"] = 1
        
        result = await self.collection.insert_one(item_dict)
        return {"id": str(result.inserted_id)}
    
    async def get_item_v1(self, item_id: str) -> Optional[dict]:
        """V1: Lấy item theo ID"""
        try:
            object_id = ObjectId(item_id)
            item = await self.collection.find_one({"_id": object_id})
            
            if item:
                item["id"] = str(item.pop("_id"))
                return item
            return None
        except Exception:
            return None
    
    # V2 Methods (Enhanced CRUD)
    async def create_item_v2(self, item_data: ItemCreateV2) -> dict:
        """V2: Tạo item với enhanced features"""
        item_dict = item_data.dict()
        item_dict["created_at"] = datetime.utcnow()
        item_dict["updated_at"] = None
        item_dict["version"] = 2
        
        result = await self.collection.insert_one(item_dict)
        return {
            "id": str(result.inserted_id),
            "created_at": item_dict["created_at"],
            "version": 2
        }
    
    async def get_item_v2(self, item_id: str) -> Optional[ItemV2]:
        """V2: Lấy item với enhanced data"""
        try:
            object_id = ObjectId(item_id)
            item = await self.collection.find_one({"_id": object_id})
            
            if item:
                item["id"] = str(item.pop("_id"))
                return ItemV2(**item)
            return None
        except Exception:
            return None
    
    async def update_item_v2(self, item_id: str, item_data: ItemUpdateV2) -> Optional[ItemV2]:
        """V2: Cập nhật item"""
        try:
            object_id = ObjectId(item_id)
            
            # Chỉ update các field không None
            update_data = {k: v for k, v in item_data.dict().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_item_v2(item_id)
            return None
        except Exception:
            return None
    
    async def delete_item_v2(self, item_id: str) -> bool:
        """V2: Xóa item"""
        try:
            object_id = ObjectId(item_id)
            result = await self.collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def list_items_v2(self, page: int = 1, per_page: int = 10, 
                           category: Optional[str] = None,
                           tags: Optional[List[str]] = None) -> dict:
        """V2: List items với pagination và filtering"""
        try:
            # Build filter query
            filter_query = {}
            if category:
                filter_query["category"] = category
            if tags:
                filter_query["tags"] = {"$in": tags}
            
            # Count total
            total = await self.collection.count_documents(filter_query)
            
            # Calculate pagination
            skip = (page - 1) * per_page
            pages = (total + per_page - 1) // per_page
            
            # Get items
            cursor = self.collection.find(filter_query).skip(skip).limit(per_page).sort("created_at", -1)
            items = []
            
            async for item in cursor:
                item["id"] = str(item.pop("_id"))
                items.append(ItemV2(**item))
            
            return {
                "items": items,
                "meta": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "pages": pages
                }
            }
        except Exception:
            return {
                "items": [],
                "meta": {"total": 0, "page": 1, "per_page": 10, "pages": 0}
            }

# Global service instance
item_service = ItemService()
