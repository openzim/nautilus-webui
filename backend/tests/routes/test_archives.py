import uuid
from http import HTTPStatus

from api.constants import constants


def test_create_archive_correct_data(logged_in_client, project_id):
    data = {
        "filename": "test_name",
        "email": "test@email.com",
        "config": {
            "title": "test_title",
            "description": "test_description",
            "name": "test_name",
            "publisher": "test_publisher",
            "creator": "test_creator",
            "languages": ["en"],
            "tags": ["test_tags"],
        },
    }
    response = logged_in_client.post(
        f"{constants.api_version_prefix}/projects/{project_id}/archives", json=data
    )
    assert response.status_code == HTTPStatus.CREATED
    json_result = response.json()
    assert uuid.UUID(json_result.get("id"))
    assert json_result.get("filename") == "test_name"
    assert json_result.get("email") == "test@email.com"
    assert json_result.get("config").get("title") == "test_title"
    assert json_result.get("config").get("description") == "test_description"
    assert json_result.get("config").get("name") == "test_name"
    assert json_result.get("config").get("publisher") == "test_publisher"
    assert json_result.get("config").get("creator") == "test_creator"
    assert json_result.get("config").get("languages")[0] == "en"
    assert json_result.get("config").get("tags")[0] == "test_tags"


def test_create_archive_wrong_authorization(client, project_id, missing_user_cookie):
    response = client.post(
        f"{constants.api_version_prefix}/projects/{project_id}/archives"
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.post(
        f"{constants.api_version_prefix}/projects/{project_id}/archives"
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_all_archive_correct_data(logged_in_client, project_id, archive_id):
    response = logged_in_client.get(
        f"{constants.api_version_prefix}/projects/{project_id}/archives"
    )
    json_result = response.json()
    assert response.status_code == HTTPStatus.OK
    assert json_result is not None
    assert len(json_result) == 1
    assert json_result[0].get("id") == str(archive_id)


def test_get_all_archive_wrong_authorization(client, missing_user_cookie, project_id):
    response = client.get(
        f"{constants.api_version_prefix}/projects/{project_id}/archives"
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.get(
        f"{constants.api_version_prefix}/projects/{project_id}/archives"
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_archive_correct_id(logged_in_client, project_id, archive_id):
    response = logged_in_client.get(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}",
    )
    json_result = response.json()
    assert response.status_code == HTTPStatus.OK
    assert uuid.UUID(json_result.get("id"))


def test_get_archive_wrong_id(logged_in_client, project_id, missing_archive_id):
    response = logged_in_client.get(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{missing_archive_id}",
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_archive_wrong_authorization(
    client, missing_user_cookie, project_id, archive_id
):
    response = client.get(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}"
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.get(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}"
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_update_archive_correct_data(logged_in_client, project_id, archive_id):
    data = {
        "filename": "test_name",
        "email": "test@email.com",
        "config": {
            "title": "test_title",
            "description": "test_description",
            "name": "test_name",
            "publisher": "test_publisher",
            "creator": "test_creator",
            "languages": ["en"],
            "tags": ["test_tags"],
        },
    }
    response = logged_in_client.patch(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}",
        json=data,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    response = logged_in_client.get(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}",
    )
    json_result = response.json()
    assert json_result.get("filename") == "test_name"
    assert json_result.get("email") == "test@email.com"
    assert json_result.get("config").get("title") == "test_title"
    assert json_result.get("config").get("description") == "test_description"
    assert json_result.get("config").get("name") == "test_name"
    assert json_result.get("config").get("publisher") == "test_publisher"
    assert json_result.get("config").get("creator") == "test_creator"
    assert json_result.get("config").get("languages")[0] == "en"
    assert json_result.get("config").get("tags")[0] == "test_tags"


def test_update_archive_wrong_id(logged_in_client, project_id, missing_archive_id):
    data = {
        "filename": "test_name",
        "email": "test@email.com",
        "config": {
            "title": "test_title",
            "description": "test_description",
            "name": "test_name",
            "publisher": "test_publisher",
            "creator": "test_creator",
            "languages": ["en"],
            "tags": ["test_tags"],
        },
    }
    response = logged_in_client.patch(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{missing_archive_id}",
        json=data,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_archive_wrong_authorization(
    client, missing_user_cookie, project_id, archive_id
):
    data = {
        "filename": "test_name",
        "email": "test@email.com",
        "config": {
            "title": "test_title",
            "description": "test_description",
            "name": "test_name",
            "publisher": "test_publisher",
            "creator": "test_creator",
            "languages": ["en"],
            "tags": ["test_tags"],
        },
    }
    response = client.patch(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}",
        json=data,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.patch(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}",
        json=data,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
