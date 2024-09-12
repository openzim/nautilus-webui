import datetime
from uuid import UUID

from sqlalchemy import func, select

from api.database import Session as DBSession
from api.database.models import File, Project, User


def get_file_by_id(file_id: UUID) -> File:
    """Get File instance by its id."""
    with DBSession.begin() as session:
        stmt = select(File).where(File.id == file_id)
        file = session.execute(stmt).scalar()
        if not file:
            raise ValueError(f"File not found: {file_id}")
        session.expunge(file)
        return file


def get_project_by_id(project_id: UUID) -> Project:
    """Get Project instance by its id."""
    with DBSession.begin() as session:
        stmt = select(Project).where(Project.id == project_id)
        project = session.execute(stmt).scalar()
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        session.expunge(project)
        return project


def ensure_user_with(id_: UUID) -> bool:
    """whether such a user has been created"""
    with DBSession.begin() as session:
        stmt = select(func.count()).select_from(User).filter_by(id=id_)
        if session.scalars(stmt).one() > 0:
            return False
        user = User(created_on=datetime.datetime.now(tz=datetime.UTC), projects=[])
        session.add(user)
        user.id = id_
        session.add(user)
    return True
