import uuid

import httpx
import pytest
from dateutil import parser
from fastapi.testclient import TestClient

from src.backend.constants import API_VERSION_PREFIX
from src.backend.entrypoint import app

NON_EXISTENT_UUID = "94e430c6-8888-456a-9440-c10e4a04627c"

client = TestClient(app)


def test_create_user():
    response = client.post(f"{API_VERSION_PREFIX}/users")
    assert response.status_code == httpx.codes.CREATED
    json_result = response.json()
    assert uuid.UUID(json_result.get("id"))
    assert parser.parse(json_result.get("created_on"))
    assert response.headers.get("set-cookie") is not None


def test_user_validation():
    response = client.post(f"{API_VERSION_PREFIX}/users/projects")
    assert response.status_code == httpx.codes.UNAUTHORIZED
    params = {"user_id": NON_EXISTENT_UUID}
    response = client.post(f"{API_VERSION_PREFIX}/users/projects", params=params)
    assert response.status_code == httpx.codes.UNAUTHORIZED


@pytest.fixture
def create_user() -> str:
    response = client.post(f"{API_VERSION_PREFIX}/users")
    json_result = response.json()
    return json_result.get("id")


def test_create_project(create_user):
    params = {"name": "test_project", "user_id": create_user}
    response = client.post(f"{API_VERSION_PREFIX}/users/projects", params=params)
    assert response.status_code == httpx.codes.CREATED
    json_result = response.json()
    assert uuid.UUID(json_result.get("id"))
    assert uuid.UUID(json_result.get("user_id"))
    assert json_result.get("name") is not None
    assert parser.parse(json_result.get("created_on"))
    assert parser.parse(json_result.get("expire_on"))


@pytest.fixture
def create_project(create_user):
    user_id = create_user
    params = {"name": "project1", "user_id": user_id}
    response = client.post(f"{API_VERSION_PREFIX}/users/projects", params=params)
    json_result = response.json()
    return (json_result.get("id"), create_user)


def test_get_all_projects(create_project):
    params = {"user_id": create_project[1]}
    response = client.get(f"{API_VERSION_PREFIX}/users/projects", params=params)
    json_result = response.json()
    assert json_result is not None
    assert len(json_result) == 1


def test_get_project(create_project):
    params = {"id": create_project[0], "user_id": create_project[1]}
    response = client.get(f"{API_VERSION_PREFIX}/users/projects/", params=params)
    json_result = response.json()
    assert uuid.UUID(json_result.get("id"))
    assert uuid.UUID(json_result.get("user_id"))
    assert json_result.get("name") is not None
    assert parser.parse(json_result.get("created_on"))
    assert parser.parse(json_result.get("expire_on"))

    params = {"id": NON_EXISTENT_UUID, "user_id": create_project[1]}
    response = client.get(f"{API_VERSION_PREFIX}/users/projects/", params=params)
    assert response.status_code == httpx.codes.NOT_FOUND


def test_update_project(create_project):
    params = {
        "name": "updated_name",
        "id": create_project[0],
        "user_id": create_project[1],
    }
    response = client.put(f"{API_VERSION_PREFIX}/users/projects", params=params)

    params = {"id": create_project[0], "user_id": create_project[1]}
    response = client.get(f"{API_VERSION_PREFIX}/users/projects/", params=params)
    json_result = response.json()
    assert json_result.get("name") == "updated_name"
