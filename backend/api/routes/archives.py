from datetime import datetime
from http import HTTPStatus
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.database import gen_session
from api.database.models import Archive, Project
from api.routes import validated_project

router = APIRouter()
class ArchiveModel(BaseModel):
    id: UUID

    project_id: UUID

    filename: str
    filesize: int
    created_on: datetime
    requested_on: datetime
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
async def get_archive(archive: Archive = Depends(validated_project)) -> ArchiveModel:
    """Get a specific archives of a project"""
    return ArchiveModel.model_validate(archive)
