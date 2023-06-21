import uuid

import httpx
from dateutil import parser
from fastapi.testclient import TestClient

from src.backend.constants import API_VERSION_PREFIX
from src.backend.entrypoint import app

client = TestClient(app)


def test_create_user():
    response = client.post(f"{API_VERSION_PREFIX}/user")
    assert response.status_code == httpx.codes.CREATED
    json_result = response.json()
    assert uuid.UUID(json_result.get("id"))
    assert parser.parse(json_result.get("created_on"))
