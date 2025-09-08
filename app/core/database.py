"""
Database connection management
"""
import motor.motor_asyncio
import redis.asyncio as aioredis
from .config import settings

class DatabaseManager:
    def __init__(self):
        self.mongo_client = None
        self.redis_client = None
        self.db = None
    
    async def connect_databases(self):
        """Kết nối đến MongoDB và Redis"""
        # MongoDB connection
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.mongo_client[settings.MONGO_DATABASE]
        
        # Redis connection
        self.redis_client = aioredis.from_url(settings.REDIS_URI, decode_responses=True)
        
        # Test connections
        await self.mongo_client.admin.command('ping')
        await self.redis_client.ping()
    
    async def disconnect_databases(self):
        """Đóng kết nối database"""
        if self.mongo_client:
            self.mongo_client.close()
        if self.redis_client:
            await self.redis_client.close()
    
    async def get_health_status(self):
        """Kiểm tra trạng thái kết nối"""
        mongo_status = "disconnected"
        redis_status = "disconnected"
        
        try:
            await self.mongo_client.admin.command('ping')
            mongo_status = "connected"
        except Exception:
            pass
        
        try:
            await self.redis_client.ping()
            redis_status = "connected"
        except Exception:
            pass
        
        return {
            "mongodb": mongo_status,
            "redis": redis_status
        }

# Global database manager instance
db_manager = DatabaseManager()
