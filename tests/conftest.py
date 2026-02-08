"""pytest の共通フィクスチャ。"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI の TestClient。DB はモックしないため、E2E では実 DB が必要。"""
    return TestClient(app)
