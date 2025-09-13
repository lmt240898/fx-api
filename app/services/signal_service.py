"""
Signal Service with Redis caching for FX API
"""

import asyncio
from typing import Dict, Any, Optional
from app.utils.logger import Logger
from app.utils.redis_client import RedisClient
from app.utils.response_handler import ResponseHandler
from app.utils.response_logger import response_logger
from app.constants import ErrorCodes
from app.services.prompt_service import PromptService
from app.services.ai_service import AIService
from app.core.config import settings


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
        
        # Cache settings - Sử dụng config từ settings
        self.cache_ttl = settings.SIGNAL_SERVICE_CACHE_TTL
        self.lock_timeout = settings.SIGNAL_SERVICE_LOCK_TIMEOUT
        self.cache_wait_timeout = settings.SIGNAL_SERVICE_CACHE_WAIT_TIMEOUT
    
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
            prompt = self.prompt_service.create_prompt_for_signal_analyst(request_data)
            if not prompt:
                return ResponseHandler.error(ErrorCodes.PROMPT_SERVICE_ERROR, details="Failed to generate prompt")
            
            # Call AI service
            ai_response = await self.ai_service.generate_response(prompt)
            if not ai_response:
                return ResponseHandler.ai_error("AI service returned empty response")
            
            # Parse AI response
            signal_data = self._parse_ai_response(ai_response)
            if not signal_data:
                return ResponseHandler.ai_error("Failed to parse AI response")
            
            # Create success response
            success_response = ResponseHandler.success(signal_data)
            
            # Log response
            try:
                symbol = request_data.get('symbol', 'UNKNOWN')
                timeframe = request_data.get('timeframe', 'UNKNOWN')
                response_logger.log_signal_response(
                    symbol=symbol,
                    timeframe=timeframe,
                    response_data=success_response,
                    request_data=request_data
                )
            except Exception as log_error:
                self.logger.warning(f"Failed to log response: {log_error}")
            
            return success_response
            
        except Exception as e:
            self.logger.error(f"Direct signal processing error: {str(e)}")
            error_response = ResponseHandler.signal_service_error(str(e))
            
            # Log error response
            try:
                symbol = request_data.get('symbol', 'UNKNOWN')
                timeframe = request_data.get('timeframe', 'UNKNOWN')
                response_logger.log_signal_response(
                    symbol=symbol,
                    timeframe=timeframe,
                    response_data=error_response,
                    request_data=request_data
                )
            except Exception as log_error:
                self.logger.warning(f"Failed to log error response: {log_error}")
            
            return error_response
    
    def _parse_ai_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """
        Parse AI response into signal data according to prompt_signal_analyst.py format
        
        Expected JSON format:
        {
            "symbol": "EURUSD",
            "signal_type": "BUY/SELL/HOLD",
            "order_type_proposed": "MARKET/LIMIT/STOP" or null,
            "entry_price_proposed": float or null,
            "stop_loss_proposed": float or null,
            "take_profit_proposed": float or null,
            "estimate_win_probability": integer (20-85) or null,
            "risk_reward_ratio": float or null,
            "trailing_stop_loss": float or null,
            "pips_to_take_profit": float or null,
            "technical_reasoning": "string"
        }
        
        Args:
            ai_response: Raw AI response string
            
        Returns:
            Parsed signal data or None
        """
        try:
            import json
            import re
            
            # Clean the response - remove any markdown formatting
            cleaned_response = ai_response.strip()
            
            # Remove markdown code blocks if present
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()
            
            # Try to extract JSON from the response
            # Look for JSON object between { and }
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = cleaned_response
            
            # Parse JSON
            signal_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["symbol", "signal_type", "technical_reasoning"]
            for field in required_fields:
                if field not in signal_data:
                    self.logger.error(f"Missing required field: {field}")
                    return None
            
            # Validate signal_type
            valid_signals = ["BUY", "SELL", "HOLD"]
            if signal_data["signal_type"] not in valid_signals:
                self.logger.error(f"Invalid signal_type: {signal_data['signal_type']}")
                return None
            
            # Validate order_type_proposed if present
            if signal_data.get("order_type_proposed"):
                valid_order_types = ["MARKET", "LIMIT", "STOP"]
                if signal_data["order_type_proposed"] not in valid_order_types:
                    self.logger.error(f"Invalid order_type_proposed: {signal_data['order_type_proposed']}")
                    return None
            
            # Validate estimate_win_probability if present
            if signal_data.get("estimate_win_probability") is not None:
                prob = signal_data["estimate_win_probability"]
                if not isinstance(prob, int) or prob < 20 or prob > 85:
                    self.logger.error(f"Invalid estimate_win_probability: {prob}")
                    return None
            
            # Log successful parsing
            self.logger.info(f"Successfully parsed AI response: {signal_data['signal_type']} for {signal_data['symbol']}")
            
            return signal_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            self.logger.error(f"Raw AI response: {ai_response[:500]}...")
            return None
        except Exception as e:
            self.logger.error(f"AI response parsing error: {str(e)}")
            self.logger.error(f"Raw AI response: {ai_response[:500]}...")
            return None
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
