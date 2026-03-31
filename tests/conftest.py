import pytest
from starlette.testclient import TestClient


@pytest.fixture
def tmp_db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def app(tmp_db_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", tmp_db_path)
    from app.main import app
    return app


@pytest.fixture
def client(app):
    return TestClient(app)
