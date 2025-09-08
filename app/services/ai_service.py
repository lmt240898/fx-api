import json
from typing import Optional

from app.models.ai_config import AIConfig, AIStrategy
from app.services.ai_providers.base import AIProviderStrategy
from app.services.ai_providers.openrouter import OpenRouterProvider

# This is a simple singleton pattern to ensure we only read the config file once.
class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            with open("app/config/ai_config.json") as f:
                data = json.load(f)
                cls._config = AIConfig(**data)
        return cls._instance

    @property
    def config(self) -> AIConfig:
        return self._config

class AIService:
    """
    Main service for interacting with AI models.
    It uses the Strategy Pattern to delegate API calls to different providers.
    """
    _provider_strategies = {
        # You can map provider names to strategies here in the future
        "default": OpenRouterProvider() 
    }

    def __init__(self, strategy_key: Optional[str] = None):
        """
        Initializes the AI service.

        Args:
            strategy_key: The key of the model strategy to use from ai_config.json.
                          If None, the default model from the config will be used.
        """
        config_loader = ConfigLoader()
        self._config = config_loader.config

        key = strategy_key or self._config.use_model
        if key not in self._config.strategies:
            raise ValueError(f"Model strategy '{key}' not found in ai_config.json.")
        
        self.strategy_config: AIStrategy = self._config.strategies[key]
        
        # In the future, you could add logic here to select a provider based on the strategy_config
        self.provider_strategy: AIProviderStrategy = self._provider_strategies["default"]

    async def generate_response(self, prompt: str) -> str:
        """
        Generates a response using the selected AI model and provider strategy.

        Args:
            prompt: The prompt to send to the model.

        Returns:
            The generated text response from the AI model.
        """
        return await self.provider_strategy.generate(
            model_name=self.strategy_config.model,
            provider_config=self.strategy_config.provider,
            prompt=prompt
        )
