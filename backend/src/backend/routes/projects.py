import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException
from httpx import codes
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.database import gen_session
from backend.database.models import Project, User

router = APIRouter(prefix="/projects")


class ProjectRequest(BaseModel):
    name: str


class ProjectModel(BaseModel):
    name: str
    id: UUID
    created_on: datetime.datetime
    expire_on: datetime.datetime | None

    model_config = ConfigDict(from_attributes=True)


async def validated_user(
    user_id: Annotated[UUID | None, Cookie()] = None,
    session: Session = Depends(gen_session),
) -> User:
    """Depends()-able User from request, ensuring it exists"""
    if not user_id:
        raise HTTPException(status_code=codes.UNAUTHORIZED, detail="Missing User ID.")
    stmt = select(User).filter_by(id=user_id)
    user = session.execute(stmt).scalar()
    if not user:
        raise HTTPException(
            status_code=codes.UNAUTHORIZED, detail=f"User Not Found, ID: {user_id}."
        )
    return user


async def validated_project(
    project_id: UUID,
    user: User = Depends(validated_user),
    session: Session = Depends(gen_session),
) -> Project:
    """Depends()-able Project from request, ensuring it exists"""
    stmt = select(Project).filter_by(id=project_id).filter_by(user_id=user.id)
    project = session.execute(stmt).scalar()
    if not project:
        raise HTTPException(codes.NOT_FOUND, f"Project not found: {project_id}")
    return project


@router.post("", response_model=ProjectModel, status_code=codes.CREATED)
async def create_project(
    project: ProjectRequest,
    user: User = Depends(validated_user),
    session: Session = Depends(gen_session),
):
    """Creates a new Project"""
    now = datetime.datetime.now(tz=datetime.UTC)
    new_project = Project(
        name=project.name,
        created_on=now,
        expire_on=None,
        files=[],
        archives=[],
    )
    user.projects.append(new_project)
    session.add(new_project)
    session.flush()
    session.refresh(new_project)
    return ProjectModel.model_validate(new_project)


@router.get("", response_model=list[ProjectModel])
async def get_all_projects(
    user: User = Depends(validated_user),
) -> list[ProjectModel]:
    """Get all projects of a user."""
    return TypeAdapter(list[ProjectModel]).validate_python(user.projects)


@router.get("/{project_id}", response_model=ProjectModel)
async def get_project(project: Project = Depends(validated_project)) -> ProjectModel:
    """Get a specific project by its id."""
    return ProjectModel.model_validate(project)


@router.delete("/{project_id}", status_code=codes.NO_CONTENT)
async def delete_project(
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
):
    """Delete a specific project by its id."""
    session.delete(project)


@router.patch("/{project_id}", status_code=codes.NO_CONTENT)
async def update_project(
    project_request: ProjectRequest,
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
):
    """Update a specific project by its id."""
    stmt = update(Project).filter_by(id=project.id).values(name=project_request.name)
    session.execute(stmt)
