import base64
import datetime
import io
from enum import Enum
from http import HTTPStatus
from typing import Any
from uuid import UUID

import zimscraperlib.image
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from zimscraperlib import filesystem

from api.constants import constants
from api.database import gen_session
from api.database.models import Archive, Project
from api.routes import (
    calculate_file_size,
    normalize_filename,
    read_file_in_chunks,
    validated_project,
)

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
    config = archive_request.config.model_dump()
    config["filename"] = normalize_filename(config.get("filename"))
    stmt = (
        update(Archive)
        .filter_by(id=archive.id)
        .values(
            email=archive_request.email,
            config=archive_request.config.model_dump(),
        )
    )
    session.execute(stmt)


def validate_illustration_image(upload_file: UploadFile):
    """
    Validates the illustration image to ensure it meets the requirements.

    Args:
        upload_file (UploadFile): The uploaded illustration image.

    Raises:
        HTTPException: If the illustration is invalid,
                       the illustration is empty,
                       illustration is not a png image.
    """
    filename = upload_file.filename

    if not filename:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Filename is invalid."
        )  # pragma: no cover

    size = calculate_file_size(upload_file.file)

    if size == 0:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Empty file.")

    if size > constants.illustration_quota:
        raise HTTPException(
            status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            detail="Illustration is too large.",
        )

    mimetype = filesystem.get_content_mimetype(upload_file.file.read(2048))

    if "image/" not in mimetype:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Illustration is not a valid image.",
        )

    upload_file.file.seek(0)


@router.post(
    "/{project_id}/archives/{archive_id}/illustration",
    status_code=HTTPStatus.CREATED,
)
async def upload_illustration(
    uploaded_illustration: UploadFile,
    archive: Archive = Depends(validated_archive),
    session: Session = Depends(gen_session),
):
    """Upload an illustration of a archive."""
    validate_illustration_image(uploaded_illustration)

    src = io.BytesIO()
    for chunk in read_file_in_chunks(uploaded_illustration.file):
        src.write(chunk)
    dst = io.BytesIO()
    try:
        zimscraperlib.image.convert_image(
            src, dst, fmt="PNG"  # pyright: ignore [reportGeneralTypeIssues]
        )
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Illustration cannot be converted to PNG",
        ) from exc

    try:
        zimscraperlib.image.resize_image(dst, width=48, height=48, method="cover")
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Illustration cannot be resized",
        ) from exc
    else:
        new_config = archive.config
        new_config["illustration"] = base64.b64encode(dst.getvalue()).decode("utf-8")
        stmt = update(Archive).filter_by(id=archive.id).values(config=new_config)
        session.execute(stmt)
