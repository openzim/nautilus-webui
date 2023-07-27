import datetime
import hashlib
import http
import os
from collections.abc import Iterator
from enum import Enum
from pathlib import Path
from typing import BinaryIO
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from httpx import codes
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from zimscraperlib import filesystem

from api.constants import BackendConf, logger
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


class FileSaveLocation(Enum):
    LOCAL = "LOCAL"
    S3 = "S3"


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


def read_file_in_chunks(
    reader: BinaryIO, chunk_size=BackendConf.chunk_size
) -> Iterator[bytes]:
    """Read Big file chunk by chunk. Default chunk size is 2k"""
    while True:
        chunk = reader.read(chunk_size)
        if not chunk:
            break
        yield chunk
    reader.seek(0)


def generate_file_hash(file: BinaryIO) -> str:
    """Generate sha256 hash of a file, optimized for large files"""
    hasher = hashlib.sha256()
    for chunk in read_file_in_chunks(file):
        hasher.update(chunk)
    return hasher.hexdigest()


def save_file(file_name: str, file: BinaryIO) -> Path:
    """Saves a binary file to a specific location and returns its path."""
    if not BackendConf.transient_storage_path.exists():
        os.makedirs(BackendConf.transient_storage_path, exist_ok=True)
    fpath = Path(BackendConf.transient_storage_path).joinpath(file_name)
    if not fpath.is_file():
        with open(fpath, "wb") as file_object:
            for chunk in read_file_in_chunks(file):
                file_object.write(chunk)
            file.seek(0)
    return fpath


def calculate_file_size(file: BinaryIO) -> int:
    size = 0
    for chunk in read_file_in_chunks(file):
        size += len(chunk)
    return size


def validate_uploaded_file(upload_file: UploadFile):
    """
    Validates the uploaded file to ensure it meets the requirements.

    Args:
        upload_file (UploadFile): The uploaded file object.

    Returns:
        tuple: A tuple containing filename, size, and mimetype of the file.

    Raises:
        HTTPException: If the filename is invalid, the file is empty.
    """
    filename = upload_file.filename
    size = calculate_file_size(upload_file.file)

    if not filename:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST, detail="Filename is invalid."
        )

    if size == 0:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST, detail="Empty file."
        )

    if size > BackendConf.project_quota:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail="Uploaded File is too large.",
        )

    mimetype = filesystem.get_content_mimetype(upload_file.file.read(2048))
    upload_file.file.seek(0)

    return (filename, size, mimetype)


def validate_project_quota(file_size: int, project: Project):
    """Validates total size of uploaded files to ensure it meets the requirements."""
    total_size = file_size + project.used_space
    if total_size > BackendConf.project_quota:
        raise HTTPException(
            status_code=codes.REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded files exceeded project quota",
        )


@router.post("/{project_id}/files", status_code=http.HTTPStatus.CREATED)
async def create_file(
    uploaded_file: UploadFile,
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
) -> FileModel:
    """
    Uploads a new file and creates a corresponding FileModel.

    Returns:

        FileModel: The created FileModel.

    Note:

        HTTPException(406, "Filename is invalid"): If the filename is invalid.

        HTTPException(406, "Emtpy File"): the file is empty.

        HTTPException(416, "Uploaded files exceeded quota"):
            the file size exceeds the maximum allowed size.
    """
    now = datetime.datetime.now(tz=datetime.UTC)

    filename, size, mimetype = validate_uploaded_file(uploaded_file)
    validate_project_quota(size, project)
    file_hash = generate_file_hash(uploaded_file.file)
    try:
        fpath = save_file(f"{project.id}-{file_hash}", uploaded_file.file)
    except Exception as exc:
        logger.error(exc)
        raise HTTPException(
            http.HTTPStatus.INTERNAL_SERVER_ERROR, "Server unable to save file."
        ) from exc

    new_file = File(
        filename=filename,
        filesize=size,
        title=filename,
        authors=None,
        description=None,
        uploaded_on=now,
        hash=file_hash,
        # TODO: Using S3 to save file.
        path=str(fpath.resolve()),
        type=mimetype,
        status=FileSaveLocation.LOCAL.value,
    )
    project.used_space += size
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
    file_location.unlink(missing_ok=True)
    session.delete(file)
