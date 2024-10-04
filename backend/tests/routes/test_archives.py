import uuid
from http import HTTPStatus

import pytest
from httpx import AsyncClient

from api.constants import constants


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
        "email": "test@email.com",
        "config": {
            "filename": "test_name",
            "title": "test_title",
            "description": "test_description",
            "name": "test_name",
            "publisher": "test_publisher",
            "creator": "test_creator",
            "languages": "en",
            "tags": ["test_tags"],
            "illustration": "",
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
    assert json_result.get("email") == "test@email.com"
    assert json_result.get("config").get("filename") == "test_name"
    assert json_result.get("config").get("title") == "test_title"
    assert json_result.get("config").get("description") == "test_description"
    assert json_result.get("config").get("name") == "test_name"
    assert json_result.get("config").get("publisher") == "test_publisher"
    assert json_result.get("config").get("creator") == "test_creator"
    assert json_result.get("config").get("languages") == "en"
    assert json_result.get("config").get("tags")[0] == "test_tags"


def test_update_archive_wrong_id(logged_in_client, project_id, missing_archive_id):
    data = {
        "email": "test@email.com",
        "config": {
            "filename": "test_name",
            "title": "test_title",
            "description": "test_description",
            "name": "test_name",
            "publisher": "test_publisher",
            "creator": "test_creator",
            "languages": "en",
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
        "email": "test@email.com",
        "config": {
            "filename": "test_name",
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


def test_upload_illustration_correct_data(
    logged_in_client, project_id, test_png_image, archive_id
):
    file = {"uploaded_illustration": test_png_image}
    response = logged_in_client.post(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}/illustration",
        files=file,
    )
    assert response.status_code == HTTPStatus.CREATED


def test_upload_illustration_other_format(logged_in_client, project_id, archive_id):
    test_image = (
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00,"
        b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    )
    file = {"uploaded_illustration": test_image}
    response = logged_in_client.post(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}/illustration",
        files=file,
    )
    assert response.status_code == HTTPStatus.CREATED


def test_upload_illustration_empty_file(logged_in_client, project_id, archive_id):
    file = {"uploaded_illustration": b""}
    response = logged_in_client.post(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}/illustration",
        files=file,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_upload_too_large_illustration(logged_in_client, project_id, archive_id):
    file = {"uploaded_illustration": b"\xff" * (constants.illustration_quota + 1)}
    response = logged_in_client.post(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}/illustration",
        files=file,
    )
    assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE


def test_upload_none_image_illustration(logged_in_client, project_id, archive_id):
    file = {"uploaded_illustration": b"\xff"}
    response = logged_in_client.post(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}/illustration",
        files=file,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_upload_illustration_without_wrong_authorization(
    client, missing_user_cookie, project_id, archive_id, test_png_image
):
    file = {"uploaded_illustration": test_png_image}
    response = client.post(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}/illustration",
        files=file,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED

    client.cookies = missing_user_cookie
    response = client.post(
        f"{constants.api_version_prefix}/projects/{project_id}/archives/{archive_id}/illustration",
        files=file,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.anyio
async def test_request_archive_not_ready(alogged_in_client, project_id, archive_id):
    response = await alogged_in_client.post(
        f"{constants.api_version_prefix}/projects/"
        f"{project_id}/archives/{archive_id}/request",
        json={"email": ""},
    )
    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.anyio
async def test_request_archive_ready(
    alogged_in_client: AsyncClient,
    archive_id,
    project_id,
    expiring_project_id,
    expiring_archive_id,
    successful_storage_upload_file,
    successful_zimfarm_request_task,
):

    response = await alogged_in_client.post(
        f"{constants.api_version_prefix}/projects/"
        f"{expiring_project_id}/archives/{expiring_archive_id}/request",
        json={"email": ""},
    )
    assert response.status_code == HTTPStatus.CREATED
