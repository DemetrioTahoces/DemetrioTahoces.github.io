"""
Centralized configuration loaded from environment variables (or CV/Chatbot/.env).
"""

from pathlib import Path
from typing import Annotated, Literal

from pydantic import AliasChoices, Field, field_validator
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
    reasoning_effort: str | None = "medium"
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

    # --- Temporary block for repeated malicious questions (see middleware/abuse_guard.py) ---
    # off: no classifier · log-only: classify and log strikes, never block · block: enforce.
    abuse_mode: Literal["off", "log-only", "block"] = "log-only"
    abuse_max_strikes: int = 3
    abuse_block_minutes: int = 60
    abuse_strike_window_hours: int = 24
    # Empty = MODEL_NAME. The classifier only sees the current message, not the CV.
    abuse_classifier_model: str = ""
    abuse_classifier_reasoning_effort: str | None = "low"
    # Shared store (Upstash Redis REST; Vercel's Upstash integration injects KV_REST_API_*).
    # Unset = fail-open: strikes are only logged and nobody is blocked.
    redis_rest_url: str = Field(default="", validation_alias=AliasChoices("UPSTASH_REDIS_REST_URL", "KV_REST_API_URL"))
    redis_rest_token: str = Field(
        default="", validation_alias=AliasChoices("UPSTASH_REDIS_REST_TOKEN", "KV_REST_API_TOKEN")
    )

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

    @field_validator("reasoning_effort", "abuse_classifier_reasoning_effort", mode="before")
    @classmethod
    def _normalize_reasoning_effort(cls, value):
        return (value or "").strip().lower() or None

    @field_validator("abuse_mode", mode="before")
    @classmethod
    def _normalize_abuse_mode(cls, value):
        return str(value).strip().lower().replace("_", "-") if isinstance(value, str) else value

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
