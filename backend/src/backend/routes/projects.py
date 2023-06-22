from datetime import datetime
from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException
from httpx import codes
from pydantic import BaseModel, parse_obj_as
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.constants import PROJECT_EXPIRE_AFTER
from backend.database import gen_session
from backend.database.models import Project, User

router = APIRouter(prefix="/projects")


class ProjectModal(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    created_on: datetime
    expire_on: datetime

    class Config:
        orm_mode = True


async def validated_user(
    user_id: Annotated[UUID | None, Cookie] = None,
    session: Session = Depends(gen_session),
) -> User:
    """Utility function to verify the existence of a user"""
    if not user_id:
        raise HTTPException(
            status_code=codes.UNAUTHORIZED, detail="Did not offer the User ID."
        )
    queried_user = session.get(User, user_id)
    if not queried_user:
        raise HTTPException(
            status_code=codes.UNAUTHORIZED, detail="User does not exit."
        )
    return queried_user


@router.post("", response_model=ProjectModal, status_code=codes.CREATED)
async def create_project(
    name: str,
    user: User = Depends(validated_user),
    session: Session = Depends(gen_session),
):
    """Post this endpoint to create a project."""
    now = datetime.utcnow()
    new_project = Project(
        name=name,
        created_on=now,
        expire_on=(now + PROJECT_EXPIRE_AFTER),
        files=[],
        archives=[],
    )
    user.projects.append(new_project)
    session.add(new_project)
    session.flush()
    session.refresh(new_project)
    return ProjectModal.from_orm(new_project)


@router.get("", response_model=List[ProjectModal])
async def get_all_projects(
    user: User = Depends(validated_user),
) -> List[ProjectModal]:
    """Get all projects of a user."""
    return parse_obj_as(List[ProjectModal], user.projects)


@router.get("/", response_model=ProjectModal)
async def get_project(
    id: UUID,
    user: User = Depends(validated_user),
    session: Session = Depends(gen_session),
) -> ProjectModal:
    """Get a specific project by its id."""
    statement = select(Project).filter_by(user_id=user.id).filter_by(id=id)
    queried_project = session.execute(statement).scalar()
    if not queried_project:
        raise HTTPException(codes.NOT_FOUND, "Not found project.")
    return ProjectModal.from_orm(queried_project)


@router.put("")
async def update_project(
    name: str,
    id: UUID,
    user: User = Depends(validated_user),
    session: Session = Depends(gen_session),
):
    """Update a specific project by its id."""
    statement = (
        update(Project).filter_by(user_id=user.id).filter_by(id=id).values(name=name)
    )
    session.execute(statement)
