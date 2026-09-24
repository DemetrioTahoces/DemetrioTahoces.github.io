from core.config import DEFAULT_ALLOWED_ORIGINS, Settings


def test_allowed_origins_accepts_comma_separated_env(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://demetriotahoces.github.io/, http://localhost:8000,,")
    settings = Settings(_env_file=None)
    assert settings.allowed_origins == ["https://demetriotahoces.github.io", "http://localhost:8000"]


def test_defaults_without_env(monkeypatch):
    for var in ("ALLOWED_ORIGINS", "REASONING_EFFORT", "MODEL_NAME"):
        monkeypatch.delenv(var, raising=False)
    settings = Settings(_env_file=None)
    assert settings.allowed_origins == DEFAULT_ALLOWED_ORIGINS
    assert settings.reasoning_effort == "low"


def test_reasoning_effort_is_normalized(monkeypatch):
    monkeypatch.setenv("REASONING_EFFORT", "  ")
    assert Settings(_env_file=None).reasoning_effort is None
    monkeypatch.setenv("REASONING_EFFORT", "Medium")
    assert Settings(_env_file=None).reasoning_effort == "medium"


def test_unknown_legacy_variables_are_ignored(monkeypatch):
    monkeypatch.setenv("PROVIDER_NAME", "OpenAI")
    Settings(_env_file=None)
