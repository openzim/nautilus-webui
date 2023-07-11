import datetime

import pytest
from fastapi.testclient import TestClient
from src.backend.entrypoint import app

from backend.database import Session
from backend.database.models import Project, User


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
