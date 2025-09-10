"""
Redis client utility for FX API
"""

import redis
import json
import time
import uuid
import os
from typing import Optional, Dict, Any
from app.utils.logger import Logger


class RedisClient:
    """Redis client with distributed locking support"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        Initialize Redis client
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
        """
        # Parse Redis URI if provided
        redis_uri = os.getenv("REDIS_URI")
        if redis_uri:
            # Parse redis://localhost:9979 format
            if redis_uri.startswith("redis://"):
                uri_parts = redis_uri[8:].split(":")
                if len(uri_parts) >= 2:
                    host = uri_parts[0]
                    port = int(uri_parts[1])
        
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.logger = Logger("redis_client")
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            self.logger.error(f"Redis connection failed: {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get value from Redis
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None
        """
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            self.logger.error(f"Redis get error for key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = 600) -> bool:
        """
        Set value in Redis with TTL
        
        Args:
            key: Cache key
            value: Data to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            json_value = json.dumps(value)
            result = self.redis_client.setex(key, ttl, json_value)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Redis set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from Redis
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.redis_client.delete(key)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Redis delete error for key {key}: {str(e)}")
            return False
    
    def acquire_lock(self, lock_key: str, timeout: int = 120, blocking_timeout: int = 0.1) -> Optional[str]:
        """
        Acquire distributed lock
        
        Args:
            lock_key: Lock key
            timeout: Lock timeout in seconds
            blocking_timeout: Blocking timeout for lock acquisition
            
        Returns:
            Lock identifier if successful, None otherwise
        """
        lock_identifier = str(uuid.uuid4())
        
        try:
            # Try to acquire lock with timeout
            result = self.redis_client.set(
                lock_key, 
                lock_identifier, 
                nx=True,  # Only set if not exists
                ex=timeout  # Expire after timeout seconds
            )
            
            if result:
                self.logger.info(f"Lock acquired: {lock_key}")
                return lock_identifier
            
            # If blocking is enabled, wait for lock
            if blocking_timeout > 0:
                start_time = time.time()
                while time.time() - start_time < blocking_timeout:
                    result = self.redis_client.set(lock_key, lock_identifier, nx=True, ex=timeout)
                    if result:
                        self.logger.info(f"Lock acquired after waiting: {lock_key}")
                        return lock_identifier
                    time.sleep(0.01)  # Wait 10ms before retry
            
            return None
            
        except Exception as e:
            self.logger.error(f"Lock acquisition error for {lock_key}: {str(e)}")
            return None
    
    def release_lock(self, lock_key: str, lock_identifier: str) -> bool:
        """
        Release distributed lock
        
        Args:
            lock_key: Lock key
            lock_identifier: Lock identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Lua script to ensure we only release our own lock
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            
            result = self.redis_client.eval(lua_script, 1, lock_key, lock_identifier)
            
            if result:
                self.logger.info(f"Lock released: {lock_key}")
                return True
            else:
                self.logger.warning(f"Lock release failed (not owner): {lock_key}")
                return False
                
        except Exception as e:
            self.logger.error(f"Lock release error for {lock_key}: {str(e)}")
            return False
    
    def wait_for_cache(self, cache_key: str, timeout: int = 120) -> Optional[Dict[str, Any]]:
        """
        Wait for cache to be populated by another process
        
        Args:
            cache_key: Cache key to wait for
            timeout: Maximum wait time in seconds
            
        Returns:
            Cached data or None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            data = self.get(cache_key)
            if data:
                self.logger.info(f"Cache found after waiting: {cache_key}")
                return data
            
            time.sleep(0.1)  # Wait 100ms before retry
        
        self.logger.warning(f"Cache wait timeout: {cache_key}")
        return None
