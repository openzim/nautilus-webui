import datetime
import hashlib
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import BinaryIO
from uuid import UUID

import magic
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from httpx import codes
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from zimscraperlib import filesystem

from api.constants import BackendConf
from api.database import gen_session
from api.database.models import File, Project
from api.routes import validated_project

router = APIRouter()


class FileMetadataUpdateRequest(BaseModel):
    filename: str
    title: str
    authors: list[str] | None
    description: str | None


class FileModel(BaseModel):
    id: UUID

    project_id: UUID
    filename: str
    filesize: int
    title: str
    authors: list[str] | None
    description: str | None
    uploaded_on: datetime.datetime
    hash: str
    type: str
    status: str

    model_config = ConfigDict(from_attributes=True)


def validated_file(
    file_id: UUID,
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
) -> File:
    """Depends()-able file from request, ensuring it exists"""
    stmt = select(File).filter_by(id=file_id).filter_by(project_id=project.id)
    file = session.execute(stmt).scalar()
    if not file:
        raise HTTPException(codes.NOT_FOUND, f"File not found: {file_id}")
    return file


def read_file_in_chunks(reader: BinaryIO, chunck_size=2048) -> Iterator[bytes]:
    """Read Big file chunk by chunk. Default chunk size is 2k"""
    while True:
        chunk = reader.read(chunck_size)
        if not chunk:
            break
        yield chunk


def generate_file_hash(file: Path) -> str:
    """Generate sha256 hash of a file, optimized for large files"""
    with open(file, "rb") as f:
        hasher = hashlib.sha256()
        for chunk in read_file_in_chunks(f):
            hasher.update(chunk)
        return hasher.hexdigest()


def upload_file(location: Path, file: BinaryIO) -> Path:
    """Saves a binary file to a specific location and returns its path."""
    if not location.exists():
        os.makedirs(location, exist_ok=True)
    file_location = Path(tempfile.NamedTemporaryFile(dir=location, delete=False).name)
    with open(file_location, "wb") as file_object:
        for chunk in read_file_in_chunks(file):
            file_object.write(chunk)
    return file_location


def validate_uploaded_file(upload_file: UploadFile):
    """
    Validates the uploaded file to ensure it meets the requirements.

    Args:
        upload_file (UploadFile): The uploaded file object.

    Returns:
        tuple: A tuple containing filename, size, and mimetype of the file.

    Raises:
        HTTPException: If the filename is invalid, the file is empty,
        or the file size exceeds the maximum allowed size.
    """
    filename = upload_file.filename
    size = upload_file.size

    if not filename:
        raise HTTPException(
            status_code=codes.NOT_ACCEPTABLE, detail="The filename is invalid."
        )

    if not size or size == 0:
        raise HTTPException(status_code=codes.NOT_ACCEPTABLE, detail="Emtpy file.")
    elif size > BackendConf.maximum_upload_file_size:
        raise HTTPException(
            status_code=codes.REQUEST_ENTITY_TOO_LARGE,
            detail="Upload file is too large.",
        )

    mimetype = filesystem.get_content_mimetype(upload_files.read(2048))

    return (filename, size, mimetype)


@router.post("/{project_id}/files", response_model=FileModel, status_code=codes.CREATED)
async def upload_files(
    uploaded_file: UploadFile,
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
) -> FileModel:
    """Upload new files"""
    now = datetime.datetime.now(tz=datetime.UTC)
    filename, size, mimetype = validate_uploaded_file(uploaded_file)
    location = upload_file(BackendConf.temp_files_location, upload_file.file)
    new_file = File(
        filename=filename,
        filesize=size,
        title=filename,
        authors=None,
        description=None,
        uploaded_on=now,
        hash=generate_file_hash(location),
        path=str(location.resolve()),
        type=mimetype,
        status="LOCAL",
    )
    project.files.append(new_file)
    session.add(new_file)
    session.flush()
    session.refresh(new_file)
    return FileModel.model_validate(new_file)


@router.get("/{project_id}/files", response_model=list[FileModel])
async def get_all_files(
    project: Project = Depends(validated_project),
) -> list[FileModel]:
    """Get all files of a project."""
    return TypeAdapter(list[FileModel]).validate_python(project.files)


@router.get("/{project_id}/files/{file_id}", response_model=FileModel)
async def get_file(file: File = Depends(validated_file)) -> FileModel:
    """Get a specific file by its id."""
    return FileModel.model_validate(file)


@router.patch("/{project_id}/files/{file_id}", status_code=codes.NO_CONTENT)
async def update_file(
    update_request: FileMetadataUpdateRequest,
    file: File = Depends(validated_file),
    session: Session = Depends(gen_session),
):
    """Update a specific file's metadata by its id."""
    stmt = (
        update(File)
        .filter_by(id=file.id)
        .values(
            filename=update_request.filename,
            title=update_request.title,
            authors=update_request.authors,
            description=update_request.description,
        )
    )
    session.execute(stmt)


@router.delete("/{project_id}/files/{file_id}", status_code=codes.NO_CONTENT)
async def delete_file(
    file: File = Depends(validated_file), session: Session = Depends(gen_session)
):
    """Delete a specific file by its id."""
    file_location = Path(file.path)
    if file_location.exists():
        os.remove(file_location)
    session.delete(file)
