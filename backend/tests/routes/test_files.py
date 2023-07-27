import uuid

from dateutil import parser
from httpx import codes

from api.constants import API_VERSION_PREFIX, BackendConf


def test_upload_file_correct_data(
    logged_in_client, project_id, test_file, test_file_hash
):
    params = {"project_id": project_id}
    file = {"uploaded_file": test_file}
    response = logged_in_client.post(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files", params=params, files=file
    )
    json_result = response.json()
    assert response.status_code == codes.CREATED
    assert json_result.get("hash") == test_file_hash


def test_upload_empty_file(logged_in_client, project_id):
    params = {"project_id": project_id}
    file = {"uploaded_file": b""}
    response = logged_in_client.post(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files", params=params, files=file
    )
    assert response.status_code == codes.NOT_ACCEPTABLE


def test_upload_too_large_file(logged_in_client, project_id):
    params = {"project_id": project_id}
    file = {"uploaded_file": b"\xff" * (BackendConf.project_quota + 1)}
    response = logged_in_client.post(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files", params=params, files=file
    )
    assert response.status_code == codes.REQUEST_ENTITY_TOO_LARGE


def test_upload_file_wrong_authorization(client, project_id, missing_user_cookie):
    response = client.post(f"{API_VERSION_PREFIX}/projects/{project_id}/files")
    assert response.status_code == codes.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.post(f"{API_VERSION_PREFIX}/projects/{project_id}/files")
    assert response.status_code == codes.UNAUTHORIZED


def test_get_all_files_correct_data(logged_in_client, project_id, file_id):
    params = {"project_id": project_id}
    response = logged_in_client.get(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files", params=params
    )
    json_result = response.json()
    assert response.status_code == codes.OK
    assert json_result is not None
    assert len(json_result) == 1
    assert json_result[0].get("id") == str(file_id)


def test_get_all_files_wrong_authorization(client, missing_user_cookie, project_id):
    response = client.get(f"{API_VERSION_PREFIX}/projects/{project_id}/files")
    assert response.status_code == codes.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.get(f"{API_VERSION_PREFIX}/projects/{project_id}/files")
    assert response.status_code == codes.UNAUTHORIZED


def test_get_file_correct_id(logged_in_client, project_id, file_id):
    params = {"project_id": project_id}
    response = logged_in_client.get(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{file_id}", params=params
    )
    json_result = response.json()
    assert response.status_code == codes.OK
    assert uuid.UUID(json_result.get("id"))
    assert parser.parse(json_result.get("uploaded_on"))
    assert not json_result.get("expire_on")


def test_get_project_wrong_id(logged_in_client, project_id, non_existent_file_id):
    params = {"project_id": project_id}
    response = logged_in_client.get(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{non_existent_file_id}",
        params=params,
    )
    assert response.status_code == codes.NOT_FOUND


def test_get_project_wrong_authorization(
    client, missing_user_cookie, file_id, project_id
):
    response = client.get(f"{API_VERSION_PREFIX}/projects/{project_id}/files/{file_id}")
    assert response.status_code == codes.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.get(f"{API_VERSION_PREFIX}/projects/{project_id}/files/{file_id}")
    assert response.status_code == codes.UNAUTHORIZED


def test_delete_file_correct_id(logged_in_client, project_id, file_id):
    # params = {"project_id": project_id, "file_id": file_id}
    response = logged_in_client.delete(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{file_id}"
    )
    assert response.status_code == codes.NO_CONTENT


def test_delete_file_wrong_id(logged_in_client, project_id, non_existent_file_id):
    params = {"project_id": project_id}
    response = logged_in_client.delete(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{non_existent_file_id}",
        params=params,
    )
    assert response.status_code == codes.NOT_FOUND


def test_delete_project_wrong_authorization(
    client, missing_user_cookie, file_id, project_id
):
    response = client.delete(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{file_id}"
    )
    assert response.status_code == codes.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.delete(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{file_id}"
    )
    assert response.status_code == codes.UNAUTHORIZED


def test_update_file_correct_data(logged_in_client, project_id, file_id):
    data = {
        "filename": "test_filename",
        "title": "test_title",
        "authors": ["test_author"],
        "description": "test_description",
    }
    params = {"project_id": project_id}
    response = logged_in_client.patch(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{file_id}",
        json=data,
        params=params,
    )

    assert response.status_code == codes.NO_CONTENT

    response = logged_in_client.get(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{file_id}", params=params
    )
    json_result = response.json()
    assert json_result.get("filename") == "test_filename"
    assert json_result.get("title") == "test_title"
    assert json_result.get("authors")[0] == "test_author"
    assert json_result.get("description") == "test_description"


def test_update_file_wrong_data(logged_in_client, project_id, non_existent_file_id):
    data = {
        "filename": "test_filename",
        "title": "test_title",
        "authors": ["test_author"],
        "description": "test_description",
    }
    params = {"project_id": project_id}
    response = logged_in_client.patch(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{non_existent_file_id}",
        json=data,
        params=params,
    )

    assert response.status_code == codes.NOT_FOUND


def test_update_file_wrong_authorization(
    client, missing_user_cookie, file_id, project_id
):
    response = client.patch(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{file_id}"
    )
    assert response.status_code == codes.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.patch(
        f"{API_VERSION_PREFIX}/projects/{project_id}/files/{file_id}"
    )
    assert response.status_code == codes.UNAUTHORIZED
