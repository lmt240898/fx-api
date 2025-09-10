"""
Signal Service with Redis caching for FX API
"""

import asyncio
from typing import Dict, Any, Optional
from app.utils.logger import Logger
from app.utils.redis_client import RedisClient
from app.utils.response_handler import ResponseHandler
from app.constants import ErrorCodes
from app.services.prompt_service import PromptService
from app.services.ai_service import AIService


class SignalService:
    """Signal analysis service with caching and distributed locking"""
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        """
        Initialize Signal Service
        
        Args:
            redis_client: Redis client instance
        """
        self.logger = Logger("signal_service")
        self.redis_client = redis_client or RedisClient()
        self.prompt_service = PromptService()
        self.ai_service = AIService()
        
        # Cache settings
        self.cache_ttl = 600  # 10 minutes
        self.lock_timeout = 120  # 2 minutes
        self.cache_wait_timeout = 120  # 2 minutes
    
    def _generate_cache_key(self, timezone: str, timeframe: str, symbol: str) -> str:
        """
        Generate cache key for signal
        
        Args:
            timezone: Timezone (e.g., GMT+3.0)
            timeframe: Timeframe (e.g., H2, H4, D1)
            symbol: Symbol (e.g., EURUSD)
            
        Returns:
            Cache key
        """
        return f"signal:{timezone}:{timeframe}:{symbol}"
    
    def _generate_lock_key(self, cache_key: str) -> str:
        """
        Generate lock key for cache key
        
        Args:
            cache_key: Cache key
            
        Returns:
            Lock key
        """
        return f"lock:{cache_key}"
    
    async def analyze_signal(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze signal with caching and distributed locking
        
        Args:
            request_data: Request data from API
            
        Returns:
            Signal analysis result
        """
        try:
            # Extract cache key components
            cache_key_data = request_data.get("cache_key", {})
            timezone = cache_key_data.get("timezone")
            timeframe = cache_key_data.get("timeframe")
            symbol = cache_key_data.get("symbol")
            
            # Validate required fields
            if not all([timezone, timeframe, symbol]):
                self.logger.error("Missing required cache key fields")
                return ResponseHandler.validation_error("cache_key")
            
            # Generate cache and lock keys
            cache_key = self._generate_cache_key(timezone, timeframe, symbol)
            lock_key = self._generate_lock_key(cache_key)
            
            self.logger.info(f"Processing signal request: {cache_key}")
            
            # Check if Redis is available
            if not self.redis_client.is_connected():
                self.logger.warning("Redis not available, processing without cache")
                return await self._process_signal_direct(request_data)
            
            # Try to get from cache first
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                self.logger.info(f"Cache hit: {cache_key}")
                return ResponseHandler.success(cached_result)
            
            self.logger.info(f"Cache miss: {cache_key}")
            
            # Try to acquire lock
            lock_identifier = self.redis_client.acquire_lock(lock_key, self.lock_timeout)
            
            if lock_identifier:
                # We got the lock, process the signal
                self.logger.info(f"Lock acquired, processing signal: {cache_key}")
                try:
                    result = await self._process_signal_direct(request_data)
                    
                    # Cache the result if successful
                    if result.get("success"):
                        cache_data = result.get("data", {})
                        cache_data["cache_key"] = cache_key
                        cache_data["timestamp"] = self._get_current_timestamp()
                        
                        self.redis_client.set(cache_key, cache_data, self.cache_ttl)
                        self.logger.info(f"Result cached: {cache_key}")
                    
                    return result
                    
                finally:
                    # Always release the lock
                    self.redis_client.release_lock(lock_key, lock_identifier)
            else:
                # Lock acquisition failed, wait for cache
                self.logger.info(f"Lock acquisition failed, waiting for cache: {cache_key}")
                cached_result = self.redis_client.wait_for_cache(cache_key, self.cache_wait_timeout)
                
                if cached_result:
                    self.logger.info(f"Cache populated by another process: {cache_key}")
                    return ResponseHandler.success(cached_result)
                else:
                    self.logger.error(f"Cache wait timeout: {cache_key}")
                    return ResponseHandler.redis_lock_timeout()
                    
        except Exception as e:
            self.logger.error(f"Signal analysis error: {str(e)}")
            return ResponseHandler.signal_service_error(str(e))
    
    async def _process_signal_direct(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process signal directly without cache (fallback)
        
        Args:
            request_data: Request data
            
        Returns:
            Signal analysis result
        """
        try:
            # Generate prompt
            prompt = await self.prompt_service.generate_signal_prompt(request_data)
            if not prompt:
                return ResponseHandler.error(ErrorCodes.PROMPT_SERVICE_ERROR, details="Failed to generate prompt")
            
            # Call AI service
            ai_response = await self.ai_service.analyze_signal(prompt)
            if not ai_response:
                return ResponseHandler.ai_error("AI service returned empty response")
            
            # Parse AI response
            signal_data = self._parse_ai_response(ai_response)
            if not signal_data:
                return ResponseHandler.ai_error("Failed to parse AI response")
            
            return ResponseHandler.success(signal_data)
            
        except Exception as e:
            self.logger.error(f"Direct signal processing error: {str(e)}")
            return ResponseHandler.signal_service_error(str(e))
    
    def _parse_ai_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """
        Parse AI response into signal data
        
        Args:
            ai_response: Raw AI response
            
        Returns:
            Parsed signal data or None
        """
        try:
            # This is a placeholder - implement based on actual AI response format
            # For now, return a mock response
            return {
                "signal": "BUY",
                "entry_price": 1.17417,
                "stop_loss": 1.16917,
                "take_profit": 1.17917,
                "confidence": 0.85,
                "reasoning": "AI analysis result"
            }
        except Exception as e:
            self.logger.error(f"AI response parsing error: {str(e)}")
            return None
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
