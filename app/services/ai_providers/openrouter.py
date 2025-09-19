import httpx
import json
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

from .base import AIProviderStrategy
from app.models.ai_config import AIProviderConfig
from app.core.config import settings
from app.utils.logger import Logger

class OpenRouterProvider(AIProviderStrategy):
    """Strategy for interacting with a generic AI provider API like OpenRouter."""
    
    def __init__(self):
        self.logger = Logger("openrouter_provider")

    @retry(
        stop=stop_after_attempt(settings.AI_PROVIDER_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=settings.AI_PROVIDER_RETRY_MIN_WAIT, max=settings.AI_PROVIDER_RETRY_MAX_WAIT),
        reraise=True
    )
    async def generate(
        self,
        model_name: str,
        provider_config: Optional[AIProviderConfig],
        prompt: str
    ) -> str:
        api_key = settings.AI_API_KEY
        if not api_key:
            raise ValueError("AI_API_KEY environment variable not set.")

        # Use the endpoint directly (already includes /chat/completions)
        api_url = settings.AI_API_ENDPOINT

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        system_prompt = (
            "You are a genius in technical analysis for forex trading, a risk management expert"
        )

        body = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,
            # "max_tokens": 10000
        }

        if provider_config:
            if provider_config.order:
                body["provider"] = {"order": provider_config.order}
            # Add other provider-specific logic here as needed

        # Log request body
        self._log_request_body(body, model_name)

        try:
            async with httpx.AsyncClient(timeout=settings.AI_PROVIDER_TIMEOUT) as client:
                response = await client.post(api_url, headers=headers, json=body)
                response.raise_for_status()
                
                data = response.json()
                print(f"Response: {data}")
                if data.get("choices") and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
                raise ValueError("API response did not contain any choices.")

        except httpx.HTTPStatusError as e:
            print(f"===> FAILED TO GET RESPONSE FROM THE AI PROVIDER 1")
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except RetryError:
            print(f"===> FAILED TO GET RESPONSE FROM THE AI PROVIDER 2")
            print(f"Failed to get response from the AI provider after multiple retries.")
            raise
        except Exception as e:
            print(f"===> FAILED TO GET RESPONSE FROM THE AI PROVIDER 3")
            print(f"An unexpected error occurred: {e}")
            raise

    def _log_request_body(self, body: dict, model_name: str):
        """
        Log request body vào log file với cấu trúc hiện tại
        
        Args:
            body: Request body dictionary
            model_name: AI model name
        """
        try:
            # Log request details
            self.logger.info(f"OpenRouter API Request - Model: {model_name}")
            self.logger.info(f"Request Body: {json.dumps(body, indent=2, ensure_ascii=False)}")
            
            # Log prompt length for monitoring
            if "messages" in body:
                total_prompt_length = sum(len(msg.get("content", "")) for msg in body["messages"])
                self.logger.info(f"Total prompt length: {total_prompt_length} characters")
                
        except Exception as e:
            self.logger.error(f"Error logging request body: {e}")
            # Don't raise exception to avoid breaking the main flow

