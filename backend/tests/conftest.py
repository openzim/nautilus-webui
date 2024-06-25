import datetime
import os
import urllib.parse
import uuid
from collections.abc import AsyncGenerator
from http import HTTPStatus
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest  # pyright: ignore [reportMissingImports]
import requests
from httpx import AsyncClient
from starlette.testclient import TestClient

from api.database import Session
from api.database.models import (
    Archive,
    ArchiveConfig,
    ArchiveStatus,
    File,
    Project,
    User,
)
from api.entrypoint import app
from api.files import save_file
from api.s3 import s3_storage

pytestmark = pytest.mark.asyncio(scope="package")


@pytest.fixture()
def user_id():
    new_user = User(created_on=datetime.datetime.now(datetime.UTC), projects=[])
    with Session.begin() as session:
        session.add(new_user)
        session.flush()
        session.refresh(new_user)
        created_id = new_user.id
    yield created_id
    with Session.begin() as session:
        user = session.get(User, created_id)
        if user:
            session.delete(user)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture(scope="module")  # pyright: ignore
async def aclient() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(app=app, base_url="http://localhost") as client:
        yield client


@pytest.fixture()
async def alogged_in_client(user_id: str):
    async with AsyncClient(app=app, base_url="http://localhost") as client:
        client.cookies = {"user_id": str(user_id)}
        yield client


@pytest.fixture
def non_existent_project_id():
    return "94e430c6-8888-456a-9440-c10e4a04627c"


@pytest.fixture
def missing_user_id():
    return "5c2ad919-4e85-48ff-b9a4-2066f4da3d58"


@pytest.fixture
def missing_user_cookie(missing_user_id):
    return {"user_id": missing_user_id}


@pytest.fixture()
def test_project_name():
    return "test_project_name"


@pytest.fixture()
def test_expiring_project_name():
    return "test_expiring_project_name"


@pytest.fixture()
def test_archive_name():
    return "test_archive_name.zim"


@pytest.fixture()
def missing_archive_id():
    return "55a345a6-20d2-40a7-b85a-7ec37e55b986"


@pytest.fixture()
def logged_in_client(client, user_id: str) -> str:
    cookie = {"user_id": str(user_id)}
    client.cookies = cookie
    return client


@pytest.fixture()
def file_id(project_id, test_file, test_file_hash):
    now = datetime.datetime.now(datetime.UTC)
    location = save_file(BytesIO(test_file), test_file_hash, project_id)
    new_file = File(
        filename="test filename",
        filesize=123,
        title="test title",
        authors=None,
        description=None,
        uploaded_on=now,
        hash=test_file_hash,
        path=str(location.resolve()),
        type="image/png",
        status="LOCAL",
    )
    with Session.begin() as session:
        project = session.get(Project, project_id)
        if project:
            project.files.append(new_file)
        session.add(new_file)
        session.flush()
        session.refresh(new_file)
        created_id = new_file.id
    yield created_id
    with Session.begin() as session:
        file = session.get(File, created_id)
        if file:
            file_location = Path(file.path)
            if file_location.exists():
                os.remove(file_location)
            session.delete(file)


@pytest.fixture
def test_file():
    return b"TDw\xd1\x01\xc8\xdfBE8\x80\x08;}6\xd3O9\xefm\xc5"


@pytest.fixture
def test_png_image():
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00"
        b"\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02\x00\x00\x00\x0bIDATx\xdacd`\x00\x00\x00\x06\x00\x020\x81\xd0/\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@pytest.fixture
def test_file_hash():
    return "9e56d33da489a4ba0fe1f02ed4b0b5984854845dfd666a92e112262b8e7ea0dc"


@pytest.fixture
def non_existent_file_id():
    return "60d5def8-1553-470d-82a8-25ec8ca3a135"


@pytest.fixture()
def project_id(test_project_name, user_id):
    now = datetime.datetime.now(datetime.UTC)
    new_project = Project(
        name=test_project_name,
        created_on=now,
        expire_on=None,
        files=[],
        archives=[],
    )
    with Session.begin() as session:
        user = session.get(User, user_id)
        if user:
            user.projects.append(new_project)
        session.add(new_project)
        session.flush()
        session.refresh(new_project)
        created_id = new_project.id
    yield created_id
    with Session.begin() as session:
        project = session.get(Project, created_id)
        if project:
            session.delete(project)


@pytest.fixture()
def expiring_project_id(test_expiring_project_name, user_id):
    now = datetime.datetime.now(datetime.UTC)
    new_project = Project(
        name=test_expiring_project_name,
        created_on=now,
        expire_on=now + datetime.timedelta(minutes=30),
        files=[],
        archives=[],
    )
    with Session.begin() as session:
        user = session.get(User, user_id)
        if user:
            user.projects.append(new_project)
        session.add(new_project)
        session.flush()
        session.refresh(new_project)
        created_id = new_project.id
    yield created_id
    with Session.begin() as session:
        project = session.get(Project, created_id)
        if project:
            session.delete(project)


@pytest.fixture()
def archive_id(test_archive_name, project_id):
    now = datetime.datetime.now(datetime.UTC)
    new_archive = Archive(
        created_on=now,
        status=ArchiveStatus.PENDING,
        config=ArchiveConfig.init_with(
            filename=test_archive_name,
            title="A Title",
            description="A Description",
            name="a_name",
            creator="a creator",
            publisher="a publisher",
            languages="eng",
            tags=[],
        ),
        filesize=None,
        requested_on=None,
        completed_on=None,
        download_url=None,
        collection_json_path=None,
        zimfarm_task_id=None,
        email=None,
    )
    with Session.begin() as session:
        project = session.get(Project, project_id)
        if project:
            project.archives.append(new_archive)
        session.add(new_archive)
        session.flush()
        session.refresh(new_archive)
        created_id = new_archive.id
    yield created_id
    with Session.begin() as session:
        archive = session.get(Archive, created_id)
        if archive:
            session.delete(archive)


@pytest.fixture()
def expiring_archive_id(test_archive_name, expiring_project_id):
    now = datetime.datetime.now(datetime.UTC)
    new_archive = Archive(
        created_on=now,
        status=ArchiveStatus.PENDING,
        config=ArchiveConfig.init_with(
            filename=test_archive_name,
            title="A Title",
            description="A Description",
            name="a_name",
            creator="a creator",
            publisher="a publisher",
            languages="eng",
            tags=[],
        ),
        filesize=None,
        requested_on=None,
        completed_on=None,
        download_url=None,
        collection_json_path=None,
        zimfarm_task_id=None,
        email=None,
    )
    with Session.begin() as session:
        project = session.get(Project, expiring_project_id)
        if project:
            project.archives.append(new_archive)
        session.add(new_archive)
        session.flush()
        session.refresh(new_archive)
        created_id = new_archive.id
    yield created_id
    with Session.begin() as session:
        archive = session.get(Archive, created_id)
        if archive:
            session.delete(archive)


class SuccessStorage:

    def upload_file(*args, **kwargs): ...

    def upload_fileobj(*args, **kwargs): ...

    def set_object_autodelete_on(*args, **kwargs): ...

    def has_object(*args, **kwargs):
        return True

    def check_credentials(*args, **kwargs):
        return True

    def delete_object(*args, **kwargs): ...


@pytest.fixture
def successful_s3_upload_file(monkeypatch):
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""

    monkeypatch.setattr(s3_storage, "_storage", SuccessStorage())
    yield True


class SuccessfulRequestResponse:
    status_code = HTTPStatus.OK
    text = "text"

    @staticmethod
    def raise_for_status(): ...


class SuccessfulAuthResponse(SuccessfulRequestResponse):
    @staticmethod
    def json():
        return {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
            "eyJpc3MiOiJkaXNwYXRjaGVyIiwiZXhwIj",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "aea891db-090b-4cbb-6qer-57c0928b42e6",
        }


class ScheduleCreatedResponse(SuccessfulRequestResponse):
    status_code = HTTPStatus.CREATED

    @staticmethod
    def json():
        return {"_id": uuid.uuid4().hex}


class TaskRequestedResponse(SuccessfulRequestResponse):
    status_code = HTTPStatus.CREATED

    @staticmethod
    def json():
        return {"requested": [uuid.uuid4().hex]}


class ScheduleDeletedResponse(SuccessfulRequestResponse):

    @staticmethod
    def json():
        return {}


@pytest.fixture
def successful_zimfarm_request_task(monkeypatch):
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""

    def requests_post(**kwargs):
        uri = urllib.parse.urlparse(kwargs.get("url"))
        if uri.path == "/v1/auth/authorize":
            return SuccessfulAuthResponse()
        if uri.path == "/v1/schedules/":
            return ScheduleCreatedResponse()
        if uri.path == "/v1/requested-tasks/":
            return TaskRequestedResponse()
        raise ValueError(f"Unhandled {kwargs}")

    def requests_delete(*args, **kwargs):
        return ScheduleDeletedResponse()

    monkeypatch.setattr(requests, "post", requests_post)
    monkeypatch.setattr(requests, "delete", requests_delete)
    yield True
