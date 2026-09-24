"""
Centralized configuration loaded from environment variables (or CV/Chatbot/.env).
"""

from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ALLOWED_ORIGINS = [
    "https://demetriotahoces.github.io",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


class Settings(BaseSettings):
    """Application settings. Env var names are the upper-case field names."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Model (OpenAI Responses API) ---
    api_key: str = ""
    model_name: str = "gpt-6-luna"
    # none | low | medium | high ... Empty = provider default.
    reasoning_effort: str | None = "low"
    # Cap per model call; on reasoning models it includes reasoning tokens.
    max_output_tokens: int = 2000
    request_timeout: float = 30.0

    # --- Agent guardrails (per request) ---
    max_model_calls: int = 3
    max_tool_calls: int = 2
    max_history_messages: int = 10

    # --- Rate limiting (per IP, per instance) ---
    rate_limit_per_minute: int = 5
    rate_limit_per_hour: int = 20

    # --- CORS: comma-separated list in ALLOWED_ORIGINS ---
    allowed_origins: Annotated[list[str], NoDecode] = DEFAULT_ALLOWED_ORIGINS

    # --- Knowledge base ---
    docs_path: str = "docs"
    public_site_url: str = "https://demetriotahoces.github.io"

    log_level: str = "INFO"

    # --- Optional LangSmith tracing (off unless LANGSMITH_TRACING=true) ---
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "cv-chatbot"

    @field_validator("reasoning_effort", mode="before")
    @classmethod
    def _normalize_reasoning_effort(cls, value):
        return (value or "").strip().lower() or None

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _split_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("public_site_url", mode="after")
    @classmethod
    def _strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")


settings = Settings()
