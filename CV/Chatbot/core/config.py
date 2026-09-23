"""
Centralized configuration loaded from environment variables.
"""

import os
from pydantic import field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Required ---
    api_key: str = os.getenv("API_KEY", "")

    # --- Model ---
    provider_name: str = os.getenv("PROVIDER_NAME", "gemini").lower()
    model_name: str = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")
    # Only applies to OpenAI reasoning models (gpt-5.x). Empty = provider default.
    reasoning_effort: str | None = os.getenv("REASONING_EFFORT")

    # --- Rate Limiting ---
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))
    rate_limit_per_hour: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "20"))

    # --- CORS ---
    allowed_origins: list[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "https://demetriotahoces.github.io,http://localhost:3000,http://localhost:8000",
    ).split(",")

    # --- Logging ---
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # --- Docs path (relative to project root) ---
    docs_path: str = os.getenv("DOCS_PATH", "docs")

    @field_validator("reasoning_effort", mode="before")
    @classmethod
    def _normalize_reasoning_effort(cls, value):
        return (value or "").strip().lower() or None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
