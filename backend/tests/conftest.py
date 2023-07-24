import datetime
import os
from pathlib import Path
from _pytest.tmpdir import tmp_path_factory

import pytest
from fastapi.testclient import TestClient

from api.database import Session
from api.database.models import Project, User, File
from api.entrypoint import app
from api.routes.files import upload_file
from api.constants import BackendConf


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


@pytest.fixture
def non_existent_project_id():
    return "94e430c6-8888-456a-9440-c10e4a04627c"


@pytest.fixture
def missing_user_id():
    return "5c2ad919-4e85-48ff-b9a4-2066f4da3d58"


@pytest.fixture
def missing_user_cookie(missing_user_id):
    return {"user_id": missing_user_id}


@pytest.fixture
def test_project_name():
    return "test_project_name"


@pytest.fixture()
def logged_in_client(client, user_id) -> str:
    cookie = {"user_id": str(user_id)}
    client.cookies = cookie
    return client


@pytest.fixture()
def file_id(project_id, test_file, test_file_hash):
    now = datetime.datetime.now(datetime.UTC)
    temp_file_location = BackendConf.cache_path.joinpath("files")
    location = upload_file(temp_file_location, test_file)
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
def test_file_hash():
    return "9e56d33da489a4ba0fe1f02ed4b0b5984854845dfd666a92e112262b8e7ea0dc"

@pytest.fixture
def non_existent_file_id():
    return "60d5def8-1553-470d-82a8-25ec8ca3a135"

@pytest.fixture()
def project_id(test_project_name, user_id):
    now = datetime.datetime.now(datetime.UTC)
    new_project = Project(
        name=test_project_name, created_on=now, expire_on=None, files=[], archives=[]
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
        user = session.get(User, created_id)
        if user:
            session.delete(user)
