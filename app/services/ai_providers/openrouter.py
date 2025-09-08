import httpx
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

from .base import AIProviderStrategy
from app.models.ai_config import AIProviderConfig
from app.core.config import settings

class OpenRouterProvider(AIProviderStrategy):
    """Strategy for interacting with a generic AI provider API like OpenRouter."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
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

        # Construct the full URL for the chat completions endpoint
        api_url = f"{settings.AI_API_ENDPOINT.rstrip('/')}/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        system_prompt = (
            "You are a genius in technical analysis for forex trading, a risk management expert, "
            "and a master of probability and statistics. Always provide insightful, data-driven, "
            "and probabilistic answers."
        )

        body = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0
        }

        if provider_config:
            if provider_config.order:
                body["provider"] = {"order": provider_config.order}
            # Add other provider-specific logic here as needed

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(api_url, headers=headers, json=body)
                response.raise_for_status()
                
                data = response.json()
                if data.get("choices") and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
                raise ValueError("API response did not contain any choices.")

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except RetryError:
            print(f"Failed to get response from the AI provider after multiple retries.")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
