import uuid

from dateutil import parser
from httpx import codes

from backend.constants import API_VERSION_PREFIX


def test_create_project(logged_in_client, test_project_name):
    data = {"name": test_project_name}
    response = logged_in_client.post(f"{API_VERSION_PREFIX}/projects", json=data)
    assert response.status_code == codes.CREATED
    json_result = response.json()
    assert uuid.UUID(json_result.get("id"))
    assert json_result.get("name") == test_project_name
    assert parser.parse(json_result.get("created_on"))
    assert not json_result.get("expire_on")


def test_get_all_projects(logged_in_client, test_project_id):
    response = logged_in_client.get(f"{API_VERSION_PREFIX}/projects")
    json_result = response.json()
    assert json_result is not None
    assert len(json_result) == 1
    assert json_result[0].get("id") == test_project_id


def test_get_project(
    logged_in_client, test_project_id, non_existent_uuid, test_project_name
):
    response = logged_in_client.get(f"{API_VERSION_PREFIX}/projects/{test_project_id}")
    json_result = response.json()
    assert uuid.UUID(json_result.get("id"))
    assert json_result.get("name") == test_project_name
    assert parser.parse(json_result.get("created_on"))
    assert not json_result.get("expire_on")

    response = logged_in_client.get(
        f"{API_VERSION_PREFIX}/projects/{non_existent_uuid}"
    )
    assert response.status_code == codes.NOT_FOUND


def test_update_project(logged_in_client, test_project_id):
    data = {
        "name": "updated_name",
    }
    response = logged_in_client.put(
        f"{API_VERSION_PREFIX}/projects/{test_project_id}", json=data
    )

    assert response.status_code == codes.OK

    response = logged_in_client.get(f"{API_VERSION_PREFIX}/projects/{test_project_id}")
    json_result = response.json()
    assert json_result.get("name") == "updated_name"


def test_user_validation(test_client, fake_cookies, non_existent_uuid):
    # Create projects
    response = test_client.post(f"{API_VERSION_PREFIX}/projects")
    assert response.status_code == codes.UNAUTHORIZED

    test_client.cookies = fake_cookies
    response = test_client.post(f"{API_VERSION_PREFIX}/projects")
    assert response.status_code == codes.UNAUTHORIZED

    # Get all projects
    response = test_client.get(f"{API_VERSION_PREFIX}/projects")
    assert response.status_code == codes.UNAUTHORIZED

    test_client.cookies = fake_cookies
    response = test_client.get(f"{API_VERSION_PREFIX}/projects")
    assert response.status_code == codes.UNAUTHORIZED

    # Get a specific project
    response = test_client.get(f"{API_VERSION_PREFIX}/projects/{non_existent_uuid}")
    assert response.status_code == codes.UNAUTHORIZED

    test_client.cookies = fake_cookies
    response = test_client.get(f"{API_VERSION_PREFIX}/projects/{non_existent_uuid}")
    assert response.status_code == codes.UNAUTHORIZED

    # Update project
    response = test_client.put(f"{API_VERSION_PREFIX}/projects/{non_existent_uuid}")
    assert response.status_code == codes.UNAUTHORIZED

    test_client.cookies = fake_cookies
    response = test_client.put(f"{API_VERSION_PREFIX}/projects/{non_existent_uuid}")
    assert response.status_code == codes.UNAUTHORIZED
