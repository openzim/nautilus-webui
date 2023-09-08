import datetime
from enum import Enum
from http import HTTPStatus
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from api.constants import constants
from api.database import gen_session
from api.database.models import Archive, Project
from api.routes import validated_project

router = APIRouter()


class ArchiveStatus(str, Enum):
    # It's in database but not requested and can be modified
    PENDING = "PENDING"
    # it has been ZF-requested; can not be modified by user,
    # awaiting callback from ZimFarm
    REQUESTED = "REQUESTED"
    # ZimFarm task succeeded, it now has a download_url and filesize
    READY = "READY"
    # ZimFarm task failed, cant be downloaded
    FAILED = "FAILED"


class ArchiveConfig(BaseModel):
    title: str | None
    description: str | None
    name: str | None
    publisher: str | None
    creator: str | None
    languages: list[str] | None
    tags: list[str] | None
    filename: str


class ArchiveRequest(BaseModel):
    email: str | None
    config: ArchiveConfig

    model_config = ConfigDict(from_attributes=True)


class ArchiveModel(BaseModel):
    id: UUID

    project_id: UUID

    filesize: int | None
    created_on: datetime.datetime
    download_url: str | None
    status: str
    email: str | None
    config: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


def validated_archive(
    archive_id: UUID,
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
) -> Archive:
    """Depends()-able archive from request, ensuring it exists"""
    stmt = select(Archive).filter_by(id=archive_id).filter_by(project_id=project.id)
    archive = session.execute(stmt).scalar()
    if not archive:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Archive not found: {archive_id}")
    return archive


@router.get("/{project_id}/archives", response_model=list[ArchiveModel])
async def get_all_archives(
    project: Project = Depends(validated_project),
) -> list[ArchiveModel]:
    """Get all archives of a project"""
    return TypeAdapter(list[ArchiveModel]).validate_python(project.archives)


@router.get("/{project_id}/archives/{archive_id}", response_model=ArchiveModel)
async def get_archive(archive: Archive = Depends(validated_archive)) -> ArchiveModel:
    """Get a specific archives of a project"""
    return ArchiveModel.model_validate(archive)


@router.patch(
    "/{project_id}/archives/{archive_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def update_archive(
    archive_request: ArchiveRequest,
    archive: Archive = Depends(validated_archive),
    session: Session = Depends(gen_session),
):
    """Update a metadata of a archive"""
    stmt = (
        update(Archive)
        .filter_by(id=archive.id)
        .values(
            email=archive_request.email,
            config=archive_request.config.model_dump(),
        )
    )
    session.execute(stmt)
