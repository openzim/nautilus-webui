import httpx
from fastapi.testclient import TestClient

from src.backend.main import app

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == httpx.codes.OK
    assert response.text == '"pong"'
