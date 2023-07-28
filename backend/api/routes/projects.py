import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from httpx import codes
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import update
from sqlalchemy.orm import Session

from api.database import gen_session
from api.database.models import Project, User
from api.routes import validated_project, validated_user

router = APIRouter(prefix="/projects")


class ProjectRequest(BaseModel):
    name: str


class ProjectModel(BaseModel):
    name: str
    id: UUID
    created_on: datetime.datetime
    expire_on: datetime.datetime | None

    model_config = ConfigDict(from_attributes=True)


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
