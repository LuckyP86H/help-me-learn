"""Application settings.

Values load from (highest precedence first): real environment variables,
backend/.env, then the defaults below. API keys stay empty when unset — a
provider without a key simply doesn't appear in the registry.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    openai_api_key: str = ""
    deepseek_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    # "openai" (requires OPENAI_API_KEY) or "mock" (offline, deterministic)
    embedding_provider: str = "openai"

    data_dir: Path = BACKEND_DIR / "data"

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "app.db"


settings = Settings()
