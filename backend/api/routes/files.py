import datetime
import hashlib
from collections.abc import Iterator
from enum import Enum
from http import HTTPStatus
from pathlib import Path
from time import sleep
from typing import BinaryIO
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session
from zimscraperlib import filesystem

from api.constants import constants, logger
from api.database import gen_session, get_local_fpath_for
from api.database.models import File, Project
from api.redis import task_queue
from api.routes import validated_project
from api.s3 import s3_storage

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


class FileStatus(Enum):
    LOCAL = "LOCAL"
    S3 = "S3"
    FAILURE = "Failure"


def validated_file(
    file_id: UUID,
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
) -> File:
    """Depends()-able file from request, ensuring it exists"""
    stmt = select(File).filter_by(id=file_id).filter_by(project_id=project.id)
    file = session.execute(stmt).scalar()
    if not file:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"File not found: {file_id}")
    return file


def read_file_in_chunks(
    reader: BinaryIO, chunk_size=constants.chunk_size
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


def save_file(file: BinaryIO, file_hash: str, project_id: UUID) -> Path:
    """Saves a binary file to a specific location and returns its path."""
    fpath = get_local_fpath_for(file_hash, project_id)
    if not fpath.is_file():
        with open(fpath, "wb") as file_object:
            for chunk in read_file_in_chunks(file):
                file_object.write(chunk)
    return fpath


def calculate_file_size(file: BinaryIO) -> int:
    """Calculate the size of a file chunk by chunk"""
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
            status_code=HTTPStatus.BAD_REQUEST, detail="Filename is invalid."
        )  # pragma: no cover

    if size == 0:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Empty file.")

    if size > constants.project_quota:
        raise HTTPException(
            status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded File is too large.",
        )

    mimetype = filesystem.get_content_mimetype(upload_file.file.read(2048))
    upload_file.file.seek(0)

    return (filename, size, mimetype)


def validate_project_quota(file_size: int, project: Project):
    """Validates total size of uploaded files to ensure it meets the requirements."""
    total_size = file_size + project.used_space
    if total_size > constants.project_quota:
        raise HTTPException(
            status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded files exceeded project quota",
        )


def s3_file_key(project_id: UUID, path: str) -> str:
    """Generate s3 file key."""
    return f"{project_id}-{path}"


def update_file_status_and_path(file: File, status: FileStatus, path: str):
    """Update file's Status and Path."""
    session = next(gen_session())
    stmt = update(File).filter_by(id=file.id).values(status=status, path=path)
    session.execute(stmt)
    session.commit()


def upload_file_to_s3(new_file: File):
    """Update local file to S3 storage and update file status"""
    s3_key = s3_file_key(new_file.project_id, new_file.hash)

    if s3_storage.storage.has_object(s3_key):
        update_file_status_and_path(new_file, FileStatus.S3, s3_key)
        return

    for i in range(constants.s3_max_tries):
        try:
            s3_storage.storage.upload_file(fpath=new_file.local_fpath, key=s3_key)
            update_file_status_and_path(new_file, FileStatus.S3, s3_key)
            new_file.local_fpath.unlink(missing_ok=True)
            return
        except Exception as exc:
            logger.error(f"{new_file.hash} failed to upload to cache: {exc}")
            logger.error(f"retry {i+1} in {constants.s3_max_tries} times")
            sleep(constants.s3_retry_wait)

    update_file_status_and_path(new_file, FileStatus.FAILURE, new_file.path)


def delete_file_from_s3(file: File):
    """Delete files from S3."""
    for i in range(constants.s3_max_tries):
        try:
            s3_storage.storage.delete_object(key=file.path)
            return
        except Exception as exc:
            logger.error(f"{file.hash} failed to delete: {exc}")
            logger.error(f"retry {i+1} in {constants.s3_max_tries} times")
            sleep(constants.s3_retry_wait)


@router.post("/{project_id}/files", status_code=HTTPStatus.CREATED)
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
        fpath = save_file(uploaded_file.file, file_hash, project.id)
    except Exception as exc:
        logger.error(exc)
        raise HTTPException(
            HTTPStatus.INTERNAL_SERVER_ERROR, "Server unable to save file."
        ) from exc

    new_file = File(
        filename=filename,
        filesize=size,
        title=filename,
        authors=None,
        description=None,
        uploaded_on=now,
        hash=file_hash,
        path=str(fpath),
        type=mimetype,
        status=FileStatus.LOCAL.value,
    )
    project.files.append(new_file)
    session.add(new_file)
    session.flush()
    session.refresh(new_file)
    task_queue.enqueue(upload_file_to_s3, new_file)
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


@router.patch("/{project_id}/files/{file_id}", status_code=HTTPStatus.NO_CONTENT)
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


@router.delete("/{project_id}/files/{file_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_file(
    file: File = Depends(validated_file), session: Session = Depends(gen_session)
):
    """Delete a specific file by its id."""
    stmt = (
        select(func.count())
        .select_from(File)
        .filter_by(project_id=file.project_id)
        .filter_by(hash=file.hash)
    )
    number_of_duplicate_files = session.scalars(stmt).one()
    if number_of_duplicate_files == 1:
        if file.status == FileStatus.LOCAL.value:
            file_location = file.local_fpath
            file_location.unlink(missing_ok=True)
        if file.status == FileStatus.S3.value:
            task_queue.enqueue(delete_file_from_s3, file)
    session.delete(file)
