import uuid

from dateutil import parser
from httpx import codes

from backend.constants import API_VERSION_PREFIX


def test_create_project_correct_data(logged_in_client, test_project_name):
    data = {"name": test_project_name}
    response = logged_in_client.post(f"{API_VERSION_PREFIX}/projects", json=data)
    assert response.status_code == codes.CREATED
    json_result = response.json()
    assert uuid.UUID(json_result.get("id"))
    assert json_result.get("name") == test_project_name
    assert parser.parse(json_result.get("created_on"))
    assert not json_result.get("expire_on")


def test_create_project_wrong_authorization(client, missing_user_cookie):
    response = client.post(f"{API_VERSION_PREFIX}/projects")
    assert response.status_code == codes.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.post(f"{API_VERSION_PREFIX}/projects")
    assert response.status_code == codes.UNAUTHORIZED


def test_get_all_projects_correct_data(logged_in_client, project_id):
    response = logged_in_client.get(f"{API_VERSION_PREFIX}/projects")
    json_result = response.json()
    assert response.status_code == codes.OK
    assert json_result is not None
    assert len(json_result) == 1
    assert json_result[0].get("id") == str(project_id)


def test_get_all_projects_wrong_authorization(client, missing_user_cookie):
    response = client.get(f"{API_VERSION_PREFIX}/projects")
    assert response.status_code == codes.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.get(f"{API_VERSION_PREFIX}/projects")
    assert response.status_code == codes.UNAUTHORIZED


def test_get_project_correct_id(logged_in_client, project_id, test_project_name):
    response = logged_in_client.get(f"{API_VERSION_PREFIX}/projects/{project_id}")
    json_result = response.json()
    assert response.status_code == codes.OK
    assert uuid.UUID(json_result.get("id"))
    assert json_result.get("name") == test_project_name
    assert parser.parse(json_result.get("created_on"))
    assert not json_result.get("expire_on")


def test_get_project_wrong_id(logged_in_client, non_existent_project_id):
    response = logged_in_client.get(
        f"{API_VERSION_PREFIX}/projects/{non_existent_project_id}"
    )
    assert response.status_code == codes.NOT_FOUND


def test_get_project_wrong_authorization(
    client, missing_user_cookie, non_existent_project_id
):
    response = client.get(f"{API_VERSION_PREFIX}/projects/{non_existent_project_id}")
    assert response.status_code == codes.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.get(f"{API_VERSION_PREFIX}/projects/{non_existent_project_id}")
    assert response.status_code == codes.UNAUTHORIZED


def test_delete_project_correct_id(logged_in_client, project_id):
    response = logged_in_client.delete(
        f"{API_VERSION_PREFIX}/projects/{str(project_id)}"
    )
    assert response.status_code == codes.NO_CONTENT


def test_delete_project_wrong_id(logged_in_client, non_existent_project_id):
    response = logged_in_client.delete(
        f"{API_VERSION_PREFIX}/projects/{non_existent_project_id}"
    )
    assert response.status_code == codes.NOT_FOUND


def test_delete_project_wrong_authorization(
    client, missing_user_cookie, non_existent_project_id
):
    response = client.delete(f"{API_VERSION_PREFIX}/projects/{non_existent_project_id}")
    assert response.status_code == codes.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.delete(f"{API_VERSION_PREFIX}/projects/{non_existent_project_id}")
    assert response.status_code == codes.UNAUTHORIZED


def test_update_project_correct_data(logged_in_client, project_id):
    data = {
        "name": "updated_name",
    }
    response = logged_in_client.patch(
        f"{API_VERSION_PREFIX}/projects/{project_id}", json=data
    )

    assert response.status_code == codes.NO_CONTENT

    response = logged_in_client.get(f"{API_VERSION_PREFIX}/projects/{project_id}")
    json_result = response.json()
    assert json_result.get("name") == "updated_name"


def test_update_project_wrong_data(logged_in_client, non_existent_project_id):
    data = {
        "name": "updated_name",
    }
    response = logged_in_client.patch(
        f"{API_VERSION_PREFIX}/projects/{non_existent_project_id}", json=data
    )

    assert response.status_code == codes.NOT_FOUND


def test_update_project_wrong_authorization(
    client, missing_user_cookie, non_existent_project_id
):
    response = client.patch(f"{API_VERSION_PREFIX}/projects/{non_existent_project_id}")
    assert response.status_code == codes.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.patch(f"{API_VERSION_PREFIX}/projects/{non_existent_project_id}")
    assert response.status_code == codes.UNAUTHORIZED
