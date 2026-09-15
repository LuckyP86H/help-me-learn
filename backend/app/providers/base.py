"""Provider-agnostic interfaces.

Every LLM vendor is wrapped in an adapter implementing LLMProvider (and
optionally EmbeddingProvider). Nothing outside app/providers/ imports a vendor
SDK — adding a provider means one new adapter file plus a registry entry.

Message format (shared across all adapters):
    [{"role": "system" | "user" | "assistant", "content": "..."}]
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ChatResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int


class LLMProvider(ABC):
    name: str  # machine name, e.g. "openai"
    label: str  # display name, e.g. "OpenAI"
    models: list[str]  # offered models; first entry is the default

    @property
    def default_model(self) -> str:
        return self.models[0]

    @abstractmethod
    def chat(self, messages: list[dict], model: str | None = None) -> ChatResult: ...


class EmbeddingProvider(ABC):
    name: str
    dim: int

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...


def split_system(messages: list[dict]) -> tuple[str | None, list[dict]]:
    """Separate system text from the conversation — several vendors want them apart."""
    system_parts = [m["content"] for m in messages if m["role"] == "system"]
    conversation = [m for m in messages if m["role"] in ("user", "assistant")]
    return ("\n\n".join(system_parts) or None), conversation
