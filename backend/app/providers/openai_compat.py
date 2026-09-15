"""OpenAI adapter, reused for any OpenAI-compatible API (DeepSeek)."""

from openai import OpenAI

from .base import ChatResult, EmbeddingProvider, LLMProvider


class OpenAICompatProvider(LLMProvider):
    def __init__(
        self,
        name: str,
        label: str,
        api_key: str,
        models: list[str],
        base_url: str | None = None,
    ):
        self.name = name
        self.label = label
        self.models = models
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(self, messages: list[dict], model: str | None = None) -> ChatResult:
        model = model or self.default_model
        resp = self._client.chat.completions.create(model=model, messages=messages)
        usage = resp.usage
        return ChatResult(
            text=resp.choices[0].message.content or "",
            model=model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )


class OpenAIProvider(OpenAICompatProvider, EmbeddingProvider):
    embedding_model = "text-embedding-3-small"
    dim = 1536

    def __init__(self, api_key: str):
        super().__init__(
            name="openai",
            label="OpenAI",
            api_key=api_key,
            models=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.embeddings.create(model=self.embedding_model, input=texts)
        return [item.embedding for item in resp.data]


def make_deepseek(api_key: str) -> OpenAICompatProvider:
    return OpenAICompatProvider(
        name="deepseek",
        label="DeepSeek",
        api_key=api_key,
        models=["deepseek-chat", "deepseek-reasoner"],
        base_url="https://api.deepseek.com",
    )
