"""
Redis service layer
"""
from typing import Optional, Any
import json
from ..core.database import db_manager

class RedisService:
    def __init__(self):
        self.default_ttl = 3600  # 1 hour
    
    @property
    def redis(self):
        return db_manager.redis_client
    
    async def set_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache với TTL"""
        try:
            ttl = ttl or self.default_ttl
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis.setex(key, ttl, value)
            return True
        except Exception:
            return False
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            value = await self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception:
            return None
    
    async def delete_cache(self, key: str) -> bool:
        """Delete cache"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception:
            return False
    
    async def test_connection(self) -> dict:
        """Test Redis connection"""
        try:
            await self.redis.set("test_key", "test_value", ex=60)
            value = await self.redis.get("test_key")
            await self.redis.delete("test_key")
            return {
                "status": "success",
                "test_result": value,
                "message": "Redis connection successful"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Redis connection failed: {str(e)}"
            }

# Global service instance
redis_service = RedisService()
