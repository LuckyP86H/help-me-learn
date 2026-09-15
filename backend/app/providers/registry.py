"""Provider registry: only providers whose API key is configured are offered.

The mock provider is always available, so the app is fully usable with no keys.
"""

from functools import lru_cache

from ..config import settings
from .anthropic_p import AnthropicProvider
from .base import EmbeddingProvider, LLMProvider
from .gemini import GeminiProvider
from .mock import MockEmbedder, MockProvider
from .openai_compat import OpenAIProvider, make_deepseek


@lru_cache(maxsize=1)
def get_providers() -> dict[str, LLMProvider]:
    providers: dict[str, LLMProvider] = {"mock": MockProvider()}
    if settings.openai_api_key:
        providers["openai"] = OpenAIProvider(settings.openai_api_key)
    if settings.deepseek_api_key:
        providers["deepseek"] = make_deepseek(settings.deepseek_api_key)
    if settings.anthropic_api_key:
        providers["anthropic"] = AnthropicProvider(settings.anthropic_api_key)
    if settings.gemini_api_key:
        providers["gemini"] = GeminiProvider(settings.gemini_api_key)
    return providers


def get_provider(name: str) -> LLMProvider:
    providers = get_providers()
    if name not in providers:
        available = ", ".join(sorted(providers))
        raise KeyError(f"Unknown or unconfigured provider '{name}'. Available: {available}")
    return providers[name]


@lru_cache(maxsize=1)
def get_embedder() -> EmbeddingProvider:
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        provider = get_providers()["openai"]
        assert isinstance(provider, EmbeddingProvider)
        return provider
    return MockEmbedder()


def list_provider_info() -> list[dict]:
    return [
        {
            "name": p.name,
            "label": p.label,
            "models": p.models,
            "default_model": p.default_model,
        }
        for p in get_providers().values()
    ]
