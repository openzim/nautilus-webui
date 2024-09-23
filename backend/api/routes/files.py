import datetime
from enum import Enum
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session
from zimscraperlib import filesystem

from api.constants import constants, logger
from api.database import Session as DBSession
from api.database import gen_session
from api.database.models import File, Project
from api.database.utils import get_file_by_id, get_project_by_id
from api.files import calculate_file_size, generate_file_hash, save_file
from api.routes import validated_project
from api.storage import storage
from api.store import task_queue

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


class FileStatus(str, Enum):
    LOCAL = "LOCAL"
    STORAGE = "STORAGE"
    FAILURE = "FAILURE"
    PROCESSING = "PROCESSING"


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


def update_file_status_and_path(file: File, status: str, path: str):
    """Update file's Status and Path."""
    with DBSession.begin() as session:
        stmt = update(File).filter_by(id=file.id).values(status=status, path=path)
        session.execute(stmt)
        session.commit()


def update_file_status(file: File, status: str):
    """Update file's Status."""
    update_file_status_and_path(file, status, file.path)


def update_file_path(file: File, path: str):
    """Update file's path."""
    update_file_status_and_path(file, file.status, path)


def upload_file_to_storage(new_file_id: UUID):
    """Update local file to Storage and update file status"""
    new_file = get_file_by_id(new_file_id)
    project = get_project_by_id(new_file.project_id)
    if not project.expire_on:
        raise ValueError(f"Project: {project.id} does not have expire date.")

    if new_file.status == FileStatus.PROCESSING:
        return
    else:
        update_file_status(new_file, FileStatus.PROCESSING)

    try:
        storage_path = storage.get_file_path(file=new_file)
        if storage.has(storage_path):
            logger.debug(
                f"Object `{storage_path}` for File {new_file_id} already in Storage"
            )
            update_file_status_and_path(new_file, FileStatus.STORAGE, storage_path)
            return
        logger.debug(
            f"Uploading {new_file_id}: `{new_file.local_fpath}` to `{storage_path}`"
        )
        storage.upload_file(fpath=new_file.local_fpath, path=storage_path)
        logger.debug(f"Uploaded {new_file_id}. Removing `{new_file.local_fpath}`…")
        new_file.local_fpath.unlink(missing_ok=True)
        storage.set_autodelete_on(storage_path, project.expire_on)
        update_file_status_and_path(new_file, FileStatus.STORAGE, storage_path)
    except Exception as exc:
        logger.error(f"File: {new_file_id} failed to upload to Storage: {exc}")
        update_file_status(new_file, FileStatus.FAILURE)
        raise exc


def delete_from_storage(storage_path: str):
    """Delete files from Storage."""
    logger.warning(f"File: {storage_path} starts deletion from Storage")
    if not storage.has(storage_path):
        logger.debug(f"{storage_path} does not exist in Storage")
        return
    try:
        storage.delete(storage_path)
    except Exception as exc:
        logger.error(f"File: {storage_path} failed to be deleted from Storage")
        logger.exception(exc)


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

    if len(project.files) == 0:
        project.expire_on = now + constants.project_expire_after

    # adding file in an independant session that gets commited before enquing
    # so its visible by other processes (rq-worker)
    with DBSession.begin() as indep_session:
        # get project again but from this session
        project_: Project | None = indep_session.execute(
            select(Project).filter_by(id=str(project.id))
        ).scalar()
        if not project_:
            raise OSError("Failed to re-fetch Project")
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
        project_.files.append(new_file)
        indep_session.add(new_file)
        indep_session.flush()
        indep_session.refresh(new_file)
        file_id = str(new_file.id)
    # request file upload by rq-worker
    task_queue.enqueue(upload_file_to_storage, file_id, retry=constants.job_retry)

    # fetch File from DB in this session to return it
    file = session.execute(select(File).filter_by(id=file_id)).scalar()
    return FileModel.model_validate(file)


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
        if file.status == FileStatus.LOCAL:
            file.local_fpath.unlink(missing_ok=True)
        if file.status == FileStatus.STORAGE:
            task_queue.enqueue(delete_from_storage, storage.get_file_path(file=file))
        if file.status == FileStatus.PROCESSING:
            task_queue.enqueue_at(
                datetime.datetime.now(tz=datetime.UTC) + constants.s3_deletion_delay,
                delete_from_storage,
                storage.get_file_path(file=file),
            )
    session.delete(file)
