from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import scoped_session

from backend.database import Session
from backend.database.models import Project, User
from src.backend.entrypoint import app


@pytest.fixture()
def mock_user_id():
    new_user = User(created_on=datetime.utcnow(), projects=[])
    with scoped_session(Session)() as session:
        session.add(new_user)
        session.flush()
        session.refresh(new_user)
        session.commit()
        return new_user.id


@pytest.fixture()
def mock_client():
    client = TestClient(app)
    return client


@pytest.fixture
def non_existent_project_id():
    return "94e430c6-8888-456a-9440-c10e4a04627c"


@pytest.fixture
def missing_user_id():
    return "5c2ad919-4e85-48ff-b9a4-2066f4da3d58"


@pytest.fixture
def missing_user_cookie(non_existent_project_id):
    return {"user_id": non_existent_project_id}


@pytest.fixture
def test_project_name():
    return "test_project_name"


@pytest.fixture()
def logged_in_client(mock_client, mock_user_id) -> str:
    cookie = {"user_id": str(mock_user_id)}
    mock_client.cookies = cookie
    return mock_client


@pytest.fixture()
def created_project_id(test_project_name, mock_user_id):
    now = datetime.utcnow()
    new_project = Project(
        name=test_project_name, created_on=now, expire_on=None, files=[], archives=[]
    )
    with scoped_session(Session)() as session:
        user = session.get(User, mock_user_id)
        if user:
            user.projects.append(new_project)
        session.add(new_project)
        session.flush()
        session.refresh(new_project)
        session.commit()
        return new_project.id


@pytest.fixture()
def mock_project_id(created_project_id):
    yield created_project_id
    with scoped_session(Session)() as session:
        project = session.get(Project, created_project_id)
        session.delete(project)
        session.commit()
