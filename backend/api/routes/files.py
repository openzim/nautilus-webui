import datetime
import hashlib
import os
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from httpx import codes
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from api.constants import BackendConf
from api.database import gen_session
from api.database.models import File, Project
from api.routes import validated_project

router = APIRouter(prefix="/files")


class FileRequest(BaseModel):
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
        raise HTTPException(codes.NOT_FOUND, f"Project not found: {file_id}")
    return file


def upload_file(location: Path, file: bytes) -> Path:
    if not location.exists():
        os.makedirs(location, exist_ok=True)
    file_location = Path(tempfile.NamedTemporaryFile(dir=location, delete=False).name)
    with open(file_location, "wb+") as file_object:
        file_object.write(file)
    return file_location


@router.post("", response_model=list[FileModel], status_code=codes.CREATED)
async def upload_files(
    uploaded_files: list[UploadFile],
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
) -> list[FileModel]:
    """Upload new files"""
    added_files = []
    temp_file_location = BackendConf.cache_path.joinpath("files")
    for file in uploaded_files:
        binary_file = await file.read()

        location = upload_file(temp_file_location, binary_file)

        now = datetime.datetime.now(tz=datetime.UTC)
        filename = file.filename if file.filename else ""
        size = file.size if file.size else 0
        content_type = file.content_type if file.content_type else "text/plain"
        new_file = File(
            filename=filename,
            filesize=size,
            title=filename,
            authors=None,
            description=None,
            uploaded_on=now,
            hash=hashlib.sha256(binary_file).hexdigest(),
            path=str(location.resolve()),
            type=content_type,
            status="LOCAL",
        )
        project.files.append(new_file)
        session.add(new_file)
        session.flush()
        session.refresh(new_file)
        added_files.append(new_file)
    return TypeAdapter(list[FileModel]).validate_python(added_files)


@router.get("", response_model=list[FileModel])
async def get_all_files(
    project: Project = Depends(validated_project),
) -> list[FileModel]:
    """Get all files of a project."""
    return TypeAdapter(list[FileModel]).validate_python(project.files)


@router.get("/{file_id}", response_model=FileModel)
async def get_file(project: File = Depends(validated_file)) -> FileModel:
    """Get a specific file by its id."""
    return FileModel.model_validate(project)


@router.patch("/{file_id}", status_code=codes.NO_CONTENT)
async def update_file(
    file_request: FileRequest,
    file: File = Depends(validated_file),
    session: Session = Depends(gen_session),
):
    """Update a specific file's metadata by its id."""
    stmt = (
        update(File)
        .filter_by(id=file.id)
        .values(
            filename=file_request.filename,
            title=file_request.title,
            authors=file_request.authors,
            description=file_request.description,
        )
    )
    session.execute(stmt)


@router.delete("/{file_id}", status_code=codes.NO_CONTENT)
async def delete_file(
    file: File = Depends(validated_file), session: Session = Depends(gen_session)
):
    """Delete a specific file by its id."""
    file_location = Path(file.path)
    if file_location.exists():
        os.remove(file_location)
    session.delete(file)
