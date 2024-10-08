import datetime
import re
from http import HTTPStatus
from pathlib import Path
from urllib.parse import unquote, urljoin
from uuid import UUID, uuid4

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from api.constants import StorageType, constants, logger
from api.database import Session as DBSession
from api.database import gen_session
from api.database.models import (
    Archive,
    ArchiveConfig,
    ArchiveStatus,
    File,
    Project,
    User,
)
from api.routes import validated_project, validated_user
from api.routes.archives import gen_collection_for, upload_file_to_storage
from api.routes.files import FileStatus, validate_project_quota
from api.storage import storage

router = APIRouter(prefix="/projects")


class ProjectRequest(BaseModel):
    name: str


class ProjectWebdavRequest(BaseModel):
    webdav_path: str


class ProjectModel(BaseModel):
    name: str
    id: UUID
    created_on: datetime.datetime
    expire_on: datetime.datetime | None
    webdav_path: str | None

    model_config = ConfigDict(from_attributes=True)


@router.post("", response_model=ProjectModel, status_code=HTTPStatus.CREATED)
async def create_project(
    project: ProjectRequest,
    user: User = Depends(validated_user),
    session: Session = Depends(gen_session),
):
    """Creates a new Project"""
    now = datetime.datetime.now(tz=datetime.UTC)
    new_project = Project(
        name=project.name,
        created_on=now,
        expire_on=None,
        webdav_path=None,
        files=[],
        archives=[],
    )
    new_archive = Archive(
        created_on=now,
        status=ArchiveStatus.PENDING,
        config=ArchiveConfig.init_with(filename="nautilus.zim"),
        filesize=None,
        requested_on=None,
        completed_on=None,
        download_url=None,
        collection_json_path=None,
        zimfarm_task_id=None,
        email=None,
    )
    user.projects.append(new_project)
    new_project.archives.append(new_archive)
    session.add(new_project)
    session.add(new_archive)
    session.flush()
    session.refresh(new_project)
    return ProjectModel.model_validate(new_project)


@router.get("", response_model=list[ProjectModel])
async def get_all_projects(
    user: User = Depends(validated_user),
) -> list[ProjectModel]:
    """Get all projects of a user."""
    return TypeAdapter(list[ProjectModel]).validate_python(user.projects)


@router.get("/{project_id}", response_model=ProjectModel)
async def get_project(project: Project = Depends(validated_project)) -> ProjectModel:
    """Get a specific project by its id."""
    return ProjectModel.model_validate(project)


@router.delete("/{project_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_project(
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
):
    """Delete a specific project by its id."""
    session.delete(project)


@router.patch("/{project_id}", status_code=HTTPStatus.NO_CONTENT)
async def update_project(
    project_request: ProjectRequest,
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
):
    """Update a specific project by its id."""
    stmt = update(Project).filter_by(id=project.id).values(name=project_request.name)
    session.execute(stmt)


@router.post("/{project_id}.dav", response_model=ProjectModel)
async def update_project_webdav(
    project_request: ProjectWebdavRequest,
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
):
    """Update a project's WebDAV path and update its Files accordingly"""

    if constants.storage_type != StorageType.WEBDAV:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Storage is not WebDAV")

    # store decoded URL, removing leading and trailing slashes
    webdav_path = re.sub(
        r"/$", "", re.sub(r"^/", "", unquote(project_request.webdav_path))
    )

    if ".." in webdav_path:
        raise HTTPException(HTTPStatus.FORBIDDEN, "Directory traversal not allowed")

    stmt = update(Project).filter_by(id=project.id).values(webdav_path=webdav_path)
    session.execute(stmt)
    session.refresh(project)

    # update Files from WebDAV folder
    await update_project_files_from_webdav(session, project)

    session.refresh(project)
    return ProjectModel.model_validate(project)


class NautilusCollection:
    def __init__(self, data: list[dict[str, str | list[str]]]):
        self.data = data
        self.files_indexes: dict[str, int] = {}
        for index, entry in enumerate(self.data):
            for fileentry in entry.get("files", []):
                if isinstance(fileentry, str):
                    filename = fileentry
                else:
                    filename = fileentry["filename"]
                self.files_indexes[filename] = index

    def __getitem__(self, key: str):
        return self.data[self.files_indexes[key]]

    def __len__(self):
        return len(self.files_indexes)

    def __contains__(self, item: str):
        return item in self.files_indexes

    def __iter__(self):
        return iter(self.data)

    def get(self, key: str, default=None):
        try:
            return self[key]
        except KeyError:
            return default


async def read_remote_collection(url: str):
    resp = requests.get(url, timeout=constants.webdav_request_timeout_sec)
    resp.raise_for_status()
    return NautilusCollection(resp.json())


async def update_project_files_from_webdav(session: Session, project: Project):
    if project.webdav_path is None:
        logger.warning(
            f"[project #{project.id}] requested webdav update "
            "but project has no webdav_path"
        )
        return

    logger.debug(f"[project #{project.id}] refreshing from {project.webdav_path}")

    now = datetime.datetime.now(tz=datetime.UTC)
    prefix = Path(project.webdav_path)

    # create a folder if this prefix does not exists
    if not storage.has(path=project.webdav_path):
        logger.debug(f"[project #{project.id}] mkdir {project.webdav_path}")
        storage.mkdir(path=project.webdav_path)

    entries = {
        str(Path(entry.path).relative_to(prefix)): entry
        for entry in list(storage.list(prefix=project.webdav_path))
    }

    remote_paths = list(entries.keys())
    db_paths = [file.path for file in project.files]
    to_add = [path for path in remote_paths if path not in db_paths]
    to_remove = [path for path in db_paths if path not in remote_paths]

    collection = None
    if entries.get("collection.json"):
        logger.debug(f"[project #{project.id}] there is a remote collection.json")
        try:
            collection = await read_remote_collection(
                urljoin(storage.public_url, f"{prefix}/collection.json")
            )
        except Exception as exc:
            logger.warning("Failed to read collection.json")
            logger.exception(exc)
        else:
            logger.debug(f"[project #{project.id}] collection: {len(collection)} files")

    # update existing Files without removing metadata
    for path, entry in entries.items():
        if path in to_add or path in to_remove:
            continue

        logger.debug(f"[project #{project.id}] deleting {path}")
        stmt = select(File).filter_by(project_id=project.id).filter_by(path=str(path))
        file = session.execute(stmt).scalar_one()
        file.filesize = entry.size
        file.uploaded_on = entry.modified_on
        file.type = entry.mimetype
        file.status = FileStatus.STORAGE.value
        session.add(file)

    # add new files
    for path, entry in entries.items():
        if path not in to_add:
            continue

        logger.debug(f"[project #{project.id}] adding {path}")
        filepath = Path(entry.path).relative_to(prefix)
        filename = filepath.name

        # TODO
        validate_project_quota(entry.size, project)

        title, authors, description = filename, None, None
        if collection and path in collection:
            authors = str(collection[path].get("authors", "")) or authors
            if isinstance(authors, str):
                authors = [authors]
            description = str(collection[path].get("description", "")) or description
            title = str(collection[path].get("title", "")) or title

        file_hash = f"unknown:{uuid4().hex}"
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
                filesize=entry.size,
                title=title,
                authors=authors,
                description=description,
                uploaded_on=entry.modified_on,
                hash=file_hash,
                path=str(filepath),
                type=entry.mimetype,
                status=FileStatus.STORAGE.value,
            )
            project_.files.append(new_file)
            indep_session.add(new_file)
            indep_session.flush()
            indep_session.refresh(new_file)

    # delete those that dont exist anymore
    for path in to_remove:
        logger.debug(f"[project #{project.id}] deleting {path}")
        stmt = select(File).filter_by(path=path).filter_by(project_id=project.id)
        file = session.execute(stmt).scalar()
        if file:
            session.delete(file)


@router.post("/{project_id}.json", response_model=ProjectModel)
async def update_project_json_collection(project: Project = Depends(validated_project)):
    """Request the update of the WebDAV-enable project's JSON collection"""

    if constants.storage_type != StorageType.WEBDAV:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Storage is not WebDAV")

    if not constants.single_user_id:
        raise HTTPException(HTTPStatus.BAD_REQUEST, "API is not in single-user mode")

    collection, collection_file, collection_hash = gen_collection_for(project=project)
    collection_key = storage.get_companion_file_path(
        project=project, file_hash=collection_hash, suffix="collection.json"
    )

    # upload it to Storage
    upload_file_to_storage(
        project=project, file=collection_file, storage_path=collection_key
    )

    return ProjectModel.model_validate(project)
