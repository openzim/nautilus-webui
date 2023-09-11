import hashlib
from collections.abc import Iterator
from http import HTTPStatus
from pathlib import Path
from typing import Annotated, BinaryIO
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.constants import constants
from api.database import gen_session, get_local_fpath_for
from api.database.models import Project, User


async def validated_user(
    response: Response,
    user_id: Annotated[UUID | None, Cookie()] = None,
    session: Session = Depends(gen_session),
) -> User:
    """Depends()-able User from request, ensuring it exists"""
    if not user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Missing User ID."
        )
    stmt = select(User).filter_by(id=user_id)
    user = session.execute(stmt).scalar()
    stmt = select(User)
    if not user:
        # using delete_cookie to construct the cookie header
        # but passing it to HTTPException as FastAPI middleware creates Response for it
        response.delete_cookie(
            key=constants.authentication_cookie_name,
            domain=constants.cookie_domain,
            secure=True,
            httponly=True,
        )
        headers = {"set-cookie": response.headers["set-cookie"]}
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=f"User Not Found, ID: {user_id}.",
            headers=headers,
        )
    return user


async def validated_project(
    project_id: UUID,
    user: User = Depends(validated_user),
    session: Session = Depends(gen_session),
) -> Project:
    """Depends()-able Project from request, ensuring it exists"""
    stmt = select(Project).filter_by(id=project_id).filter_by(user_id=user.id)
    project = session.execute(stmt).scalar()
    if not project:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Project not found: {project_id}")
    return project


def calculate_file_size(file: BinaryIO) -> int:
    """Calculate the size of a file chunk by chunk"""
    size = 0
    for chunk in read_file_in_chunks(file):
        size += len(chunk)
    return size


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


def save_file(file: BinaryIO, file_name: str, project_id: UUID) -> Path:
    """Saves a binary file to a specific location and returns its path."""
    fpath = get_local_fpath_for(file_name, project_id)
    if not fpath.is_file():
        with open(fpath, "wb") as file_object:
            for chunk in read_file_in_chunks(file):
                file_object.write(chunk)
    return fpath


def generate_file_hash(file: BinaryIO) -> str:
    """Generate sha256 hash of a file, optimized for large files"""
    hasher = hashlib.sha256()
    for chunk in read_file_in_chunks(file):
        hasher.update(chunk)
    return hasher.hexdigest()


def normalize_filename(filename):
    # TODO: Normalize Filename
    return filename
