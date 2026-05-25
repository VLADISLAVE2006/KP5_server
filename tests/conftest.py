import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import storage


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    storage.clear()
    yield
    storage.clear()
