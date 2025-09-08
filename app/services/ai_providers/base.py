from abc import ABC, abstractmethod
from typing import Optional
from app.models.ai_config import AIProviderConfig

class AIProviderStrategy(ABC):
    """Abstract base class for all AI provider strategies."""

    @abstractmethod
    async def generate(
        self, 
        model_name: str, 
        provider_config: Optional[AIProviderConfig], 
        prompt: str
    ) -> str:
        """
        Generates a response from the AI provider.

        Args:
            model_name: The name of the model to use.
            provider_config: The provider-specific configuration.
            prompt: The prompt to send to the model.

        Returns:
            The generated text response.
        """
        pass
