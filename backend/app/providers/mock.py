"""Offline provider + embedder: the whole app works with zero API keys."""

import hashlib
import re

import numpy as np

from .base import ChatResult, EmbeddingProvider, LLMProvider, split_system


def _rough_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class MockProvider(LLMProvider):
    name = "mock"
    label = "Mock (offline)"
    models = ["mock-small", "mock-large"]

    def chat(self, messages: list[dict], model: str | None = None) -> ChatResult:
        model = model or self.default_model
        system, conversation = split_system(messages)
        last_user = next(
            (m["content"] for m in reversed(conversation) if m["role"] == "user"), ""
        )
        prompt_head = last_user.strip().replace("\n", " ")[:220]
        if system and "summar" in system.lower():
            text = (
                f"[{self.name}:{model}] Mock summary — the key points of the provided "
                f"text (offline placeholder): it begins with “{prompt_head}…”. "
                "Set a real API key to get genuine analysis."
            )
        else:
            text = (
                f"[{self.name}:{model}] Mock reply to: “{prompt_head}…” — "
                "offline placeholder response. Set a real API key for genuine answers."
            )
        input_tokens = sum(_rough_tokens(m["content"]) for m in messages)
        return ChatResult(
            text=text,
            model=model,
            input_tokens=input_tokens,
            output_tokens=_rough_tokens(text),
        )


class MockEmbedder(EmbeddingProvider):
    """Deterministic hashed bag-of-words vectors.

    Not semantic, but lexically overlapping texts score closer, which makes
    offline retrieval demos behave sensibly.
    """

    name = "mock"
    dim = 256

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            v = np.zeros(self.dim, dtype=np.float32)
            for token in re.findall(r"[a-z0-9']+", text.lower()):
                h = int(hashlib.md5(token.encode()).hexdigest(), 16)
                v[h % self.dim] += 1.0
            norm = float(np.linalg.norm(v)) or 1.0
            vectors.append((v / norm).tolist())
        return vectors
