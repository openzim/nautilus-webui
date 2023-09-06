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
    CREATED = "CREATED"
    REQUEST = "REQUEST"
    FINISHED = "FINISHED"
    FAILURE = "FAILURE"


class ArchiveConfig(BaseModel):
    title: str | None
    description: str | None
    name: str | None
    publisher: str | None
    creator: str | None
    languages: list[str] | None
    tags: list[str] | None


class ArchiveRequest(BaseModel):
    filename: str | None
    email: str | None
    config: ArchiveConfig

    model_config = ConfigDict(from_attributes=True)


class ArchiveModel(BaseModel):
    id: UUID

    project_id: UUID

    filename: str
    filesize: int
    created_on: datetime.datetime
    requested_on: datetime.datetime
    download_url: str
    collection_json_path: str
    status: str
    email: str | None
    config: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


def validated_archive(
    archive_id: UUID,
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
) -> Archive:
    """Depends()-able file from request, ensuring it exists"""
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


@router.post(
    "/{project_id}/archives",
    response_model=ArchiveModel,
    status_code=HTTPStatus.CREATED,
)
async def create_archive(
    archive_request: ArchiveRequest,
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
) -> ArchiveModel:
    """Create a pre-request archive"""
    now = datetime.datetime.now(tz=datetime.UTC)
    new_archive = Archive(
        filename=archive_request.filename
        if archive_request.filename
        else f"{project.name}.zim",
        filesize=project.used_space,
        created_on=now,
        requested_on=datetime.datetime.min,
        download_url="",
        collection_json_path="",
        status=ArchiveStatus.CREATED,
        zimfarm_task_id=constants.empty_uuid,
        email=archive_request.email,
        config=archive_request.config.model_dump(),
    )
    project.archives.append(new_archive)
    session.add(new_archive)
    session.flush()
    session.refresh(new_archive)
    return ArchiveModel.model_validate(new_archive)


@router.patch(
    "/{project_id}/archives/{archive_id}",
    status_code=HTTPStatus.NO_CONTENT,
)
async def update_archive(
    archive_request: ArchiveRequest,
    archive: Archive = Depends(validated_archive),
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
):
    """Create a pre-request archive"""
    stmt = (
        update(Archive)
        .filter_by(id=archive.id)
        .values(
            filename=archive_request.filename
            if archive_request.filename
            else f"{project.name}.zim",
            email=archive_request.email,
            config=archive_request.config.model_dump(),
        )
    )
    session.execute(stmt)
