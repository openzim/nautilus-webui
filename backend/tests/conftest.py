import pytest
from fastapi.testclient import TestClient

from backend.constants import API_VERSION_PREFIX
from src.backend.entrypoint import app


@pytest.fixture()
def test_client():
    client = TestClient(app)
    return client


@pytest.fixture
def non_existent_uuid():
    return "94e430c6-8888-456a-9440-c10e4a04627c"


@pytest.fixture
def fake_cookies(non_existent_uuid):
    return {"user_id": non_existent_uuid}


@pytest.fixture
def test_project_name():
    return "test_project_name"


@pytest.fixture()
def logged_in_client(test_client) -> str:
    response = test_client.post(f"{API_VERSION_PREFIX}/users")
    test_client.cookies = response.cookies
    return test_client


@pytest.fixture()
def test_project_id(logged_in_client, test_project_name):
    data = {"name": test_project_name}
    response = logged_in_client.post(f"{API_VERSION_PREFIX}/projects", json=data)
    json_result = response.json()
    return json_result.get("id")
