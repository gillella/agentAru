from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
import yaml
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)


class ModelConfig(BaseModel):
    name: str
    display_name: str
    context_window: int
    cost_per_1k_tokens: Optional[Dict[str, float]] = None
    local: bool = False
    capabilities: List[str] = []


class ModelManager:
    """Centralized model management with easy switching"""

    def __init__(self, config_path: str = "src/config/models.yaml"):
        self.config_path = Path(config_path)
        self.models: Dict[str, Dict[str, ModelConfig]] = {}
        self._load_configs()
        self._current_model = None
        self._model_cache: Dict[str, Any] = {}

    def _load_configs(self):
        """Load model configurations from YAML"""
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)

            for provider, models in config["models"].items():
                self.models[provider] = {
                    m["name"]: ModelConfig(**m) for m in models
                }
            logger.info(f"Loaded {sum(len(m) for m in self.models.values())} model configs")
        except Exception as e:
            logger.error(f"Failed to load model configs: {e}")
            raise

    def get_model(
        self, model_name: str = None, temperature: float = 0.7, **kwargs
    ):
        """Get LangChain model instance with auto-detection and caching"""

        if not model_name:
            model_name = self._get_default_model()

        # Check cache
        cache_key = f"{model_name}_{temperature}_{str(kwargs)}"
        if cache_key in self._model_cache:
            logger.debug(f"Using cached model: {model_name}")
            return self._model_cache[cache_key]

        # Parse provider and model
        if "/" in model_name:
            provider, model_id = model_name.split("/", 1)
        else:
            provider, model_id = self._detect_provider(model_name)

        # Verify API keys
        self._check_api_key(provider)

        # Create model instance
        try:
            if provider == "anthropic":
                model = ChatAnthropic(
                    model=model_id, temperature=temperature, **kwargs
                )
            elif provider == "openai":
                model = ChatOpenAI(
                    model=model_id, temperature=temperature, **kwargs
                )
            elif provider == "ollama":
                model = ChatOllama(
                    model=model_id, temperature=temperature, **kwargs
                )
            else:
                raise ValueError(f"Unknown provider: {provider}")

            # Cache the model
            self._model_cache[cache_key] = model
            logger.info(f"Created model instance: {provider}/{model_id}")
            return model

        except Exception as e:
            logger.error(f"Failed to create model {provider}/{model_id}: {e}")
            raise

    def _detect_provider(self, model_name: str) -> tuple[str, str]:
        """Auto-detect provider from model name"""
        for provider, models in self.models.items():
            if model_name in models:
                return provider, model_name
        raise ValueError(f"Model {model_name} not found in configs")

    def _get_default_model(self) -> str:
        """Get default model from environment"""
        return os.getenv("DEFAULT_MODEL", "anthropic/claude-3-5-sonnet-20241022")

    def _check_api_key(self, provider: str):
        """Verify API key exists for provider"""
        key_map = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
        }

        if provider in key_map:
            key_name = key_map[provider]
            if not os.getenv(key_name):
                raise ValueError(
                    f"Missing API key: {key_name} required for {provider} models"
                )

    def list_models(self, provider: str = None) -> List[ModelConfig]:
        """List available models"""
        if provider:
            return list(self.models.get(provider, {}).values())

        all_models = []
        for provider_models in self.models.values():
            all_models.extend(provider_models.values())
        return all_models

    def get_model_info(self, model_name: str) -> ModelConfig:
        """Get model configuration"""
        provider, model_id = self._detect_provider(model_name)
        return self.models[provider][model_id]

    def switch_model(self, new_model: str, temperature: float = 0.7, **kwargs):
        """Switch to a different model"""
        self._current_model = self.get_model(new_model, temperature, **kwargs)
        logger.info(f"Switched to model: {new_model}")
        return self._current_model

    def clear_cache(self):
        """Clear model cache"""
        self._model_cache.clear()
        logger.info("Model cache cleared")
