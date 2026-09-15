"""Google Gemini adapter (google-genai SDK)."""

from google import genai
from google.genai import types

from .base import ChatResult, LLMProvider, split_system


class GeminiProvider(LLMProvider):
    name = "gemini"
    label = "Google Gemini"
    models = ["gemini-2.5-flash", "gemini-2.5-pro"]

    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)

    def chat(self, messages: list[dict], model: str | None = None) -> ChatResult:
        model = model or self.default_model
        system, conversation = split_system(messages)
        contents = [
            types.Content(
                role="user" if m["role"] == "user" else "model",
                parts=[types.Part(text=m["content"])],
            )
            for m in conversation
        ]
        config = (
            types.GenerateContentConfig(system_instruction=system) if system else None
        )
        resp = self._client.models.generate_content(
            model=model, contents=contents, config=config
        )
        usage = resp.usage_metadata
        return ChatResult(
            text=resp.text or "",
            model=model,
            input_tokens=(usage.prompt_token_count or 0) if usage else 0,
            output_tokens=(usage.candidates_token_count or 0) if usage else 0,
        )
