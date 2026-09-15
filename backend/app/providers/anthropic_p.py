"""Anthropic (Claude) adapter."""

import anthropic

from .base import ChatResult, LLMProvider, split_system


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    label = "Anthropic (Claude)"
    models = ["claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5"]

    def __init__(self, api_key: str):
        self._client = anthropic.Anthropic(api_key=api_key)

    def chat(self, messages: list[dict], model: str | None = None) -> ChatResult:
        model = model or self.default_model
        system, conversation = split_system(messages)
        kwargs: dict = {}
        if system:
            kwargs["system"] = system
        resp = self._client.messages.create(
            model=model,
            max_tokens=16000,
            messages=conversation,
            **kwargs,
        )
        text = "".join(block.text for block in resp.content if block.type == "text")
        return ChatResult(
            text=text,
            model=model,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
        )
