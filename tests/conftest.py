import pytest
from starlette.testclient import TestClient


@pytest.fixture
def tmp_db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def app(tmp_db_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", tmp_db_path)
    # Also patch the already-loaded settings singleton
    from app.config import settings
    monkeypatch.setattr(settings, "db_path", tmp_db_path)
    # Init the DB for tests
    from app.database import init_db
    init_db(tmp_db_path)
    from app.main import app
    return app


@pytest.fixture
def client(app):
    return TestClient(app)
