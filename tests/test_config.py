import os
import importlib


def test_config_defaults(monkeypatch):
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.delenv("SESSION_EXPIRY_DAYS", raising=False)
    import app.config
    importlib.reload(app.config)
    from app.config import settings
    assert settings.db_path == "sessions.db"
    assert settings.session_expiry_days == 5


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("DB_PATH", "/tmp/custom.db")
    monkeypatch.setenv("SESSION_EXPIRY_DAYS", "10")
    import app.config
    importlib.reload(app.config)
    from app.config import settings
    assert settings.db_path == "/tmp/custom.db"
    assert settings.session_expiry_days == 10
