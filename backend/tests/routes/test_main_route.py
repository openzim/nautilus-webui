from http import HTTPStatus

from fastapi.testclient import TestClient

from api.constants import constants
from api.entrypoint import app

client = TestClient(app)


def test_root():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == HTTPStatus.PERMANENT_REDIRECT


def test_ping():
    response = client.get(f"{constants.api_version_prefix}/ping")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "pong"}
