import httpx
from fastapi.testclient import TestClient

from api.constants import API_VERSION_PREFIX
from api.entrypoint import app

client = TestClient(app)


def test_root():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == httpx.codes.PERMANENT_REDIRECT


def test_ping():
    response = client.get(f"{API_VERSION_PREFIX}/ping")
    assert response.status_code == httpx.codes.OK
    assert response.json() == {"message": "pong"}
