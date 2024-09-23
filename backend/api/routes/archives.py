import base64
import datetime
import io
import json
from http import HTTPStatus
from typing import Any, BinaryIO
from uuid import UUID

import dateutil.parser
import zimscraperlib.image
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, TypeAdapter
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql.base import Executable as ExecutableStatement
from zimscraperlib import filesystem

from api.constants import constants, logger
from api.database import gen_session
from api.database.models import Archive, ArchiveConfig, ArchiveStatus, Project
from api.email import get_context, jinja_env, send_email_via_mailgun
from api.files import (
    calculate_file_size,
    generate_file_hash,
    normalize_filename,
    read_file_in_chunks,
)
from api.routes import userless_validated_project, validated_project
from api.storage import storage
from api.zimfarm import RequestSchema, WebhookPayload, request_task

router = APIRouter()


class ArchiveConfigRequest(BaseModel):
    email: str | None
    config: ArchiveConfig
    model_config = ConfigDict(from_attributes=True)


class ArchiveRequest(BaseModel):
    email: str | None


class ArchiveModel(BaseModel):
    id: UUID

    project_id: UUID

    filesize: int | None
    created_on: datetime.datetime
    requested_on: datetime.datetime | None
    completed_on: datetime.datetime | None
    download_url: str | None
    status: str
    email: str | None
    config: ArchiveConfig

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


def userless_validated_archive(
    archive_id: UUID,
    project: Project = Depends(userless_validated_project),
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
    archive_request: ArchiveConfigRequest,
    archive: Archive = Depends(validated_archive),
    session: Session = Depends(gen_session),
):
    """Update a metadata of a archive"""
    archive_request.config.filename = normalize_filename(
        archive_request.config.filename
    )
    stmt = (
        update(Archive)
        .filter_by(id=archive.id)
        .values(
            email=archive_request.email,
            config=archive_request.config,
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


def validate_main_logo_image(upload_file: UploadFile):
    """
    Validates the main_logo image to ensure it meets the requirements.

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

    # using same quota as illustration
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
        archive.config.illustration = base64.b64encode(dst.getvalue()).decode("utf-8")
        stmt = update(Archive).filter_by(id=archive.id).values(config=archive.config)
        session.execute(stmt)


@router.post(
    "/{project_id}/archives/{archive_id}/main_logo",
    status_code=HTTPStatus.CREATED,
)
async def upload_main_logo(
    uploaded_logo: UploadFile,
    archive: Archive = Depends(validated_archive),
    session: Session = Depends(gen_session),
):
    """Upload an illustration of a archive."""
    validate_main_logo_image(uploaded_logo)

    src = io.BytesIO()
    for chunk in read_file_in_chunks(uploaded_logo.file):
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

    archive.config.main_logo = base64.b64encode(dst.getvalue()).decode("utf-8")
    stmt = update(Archive).filter_by(id=archive.id).values(config=archive.config)
    session.execute(stmt)


def gen_collection_for(project: Project) -> tuple[list[dict[str, Any]], BinaryIO, str]:
    collection = []
    # project = get_project_by_id(project_id)
    for file in project.files:
        entry = {}
        if file.title:
            entry["title"] = file.title
        if file.description:
            entry["title"] = file.description
        if file.authors:
            entry["authors"] = ", ".join(file.authors)
        entry["files"] = [
            {
                "url": f"{constants.download_url}/"
                f"{storage.get_file_path(file=file)}",
                "filename": file.filename,
            }
        ]
        collection.append(entry)

    file = io.BytesIO()
    file.write(json.dumps(collection, indent=2, ensure_ascii=False).encode("UTF-8"))
    file.seek(0)

    digest = generate_file_hash(file)

    return collection, file, digest


def upload_file_to_storage(project: Project, file: BinaryIO, storage_path: str):

    try:
        if storage.has(storage_path):
            logger.debug(f"Object `{storage_path}` already in Storage… weird but OK")
            return
        logger.debug(f"Uploading file to `{storage_path}`")
        storage.upload_fileobj(fileobj=file, path=storage_path)
        storage.set_autodelete_on(storage_path, project.expire_on)
    except Exception as exc:
        logger.error(f"File failed to upload to Storage `{storage_path}`: {exc}")
        raise exc


@router.post(
    "/{project_id}/archives/{archive_id}/request", status_code=HTTPStatus.CREATED
)
async def request_archive(
    archive_request: ArchiveRequest,
    archive: Archive = Depends(validated_archive),
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
):
    # update archive email
    stmt = update(Archive).filter_by(id=archive.id).values(email=archive_request.email)
    session.execute(stmt)

    if archive.status != ArchiveStatus.PENDING:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Non-pending archive cannot be requested",
        )

    if not archive.config.is_ready():
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Project is not ready (Archive config missing mandatory metadata)",
        )

    # this should guard the creation of Archive instead !!
    if not project.expire_on:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Project is not ready (no archive or no files)",
        )

    # upload illustration
    illustration = io.BytesIO(base64.b64decode(archive.config.illustration))
    illus_key = storage.get_companion_file_path(
        project=project,
        file_hash=generate_file_hash(illustration),
        suffix="illustration.png",
    )
    illustration.seek(0)
    # upload it to Storage
    upload_file_to_storage(project=project, file=illustration, storage_path=illus_key)

    # upload main-logo
    if archive.config.main_logo:
        main_logo = io.BytesIO(base64.b64decode(archive.config.main_logo))
        main_logo_key = storage.get_companion_file_path(
            project=project,
            file_hash=generate_file_hash(main_logo),
            suffix="main-logo.png",
        )
        main_logo.seek(0)
        # upload it to Storage
        upload_file_to_storage(
            project=project, file=main_logo, storage_path=main_logo_key
        )

    # gen collection and stream
    collection, collection_file, collection_hash = gen_collection_for(project=project)
    collection_key = storage.get_companion_file_path(
        project=project, file_hash=collection_hash, suffix="collection.json"
    )

    # upload it to Storage
    upload_file_to_storage(
        project=project, file=collection_file, storage_path=collection_key
    )

    # Everything's on Storage, prepare and submit a ZF request
    request_def = RequestSchema(
        collection_url=f"{constants.download_url}/{collection_key}",
        name=archive.config.name,
        title=archive.config.title,
        description=archive.config.description,
        long_description=None,
        language=archive.config.languages,
        creator=archive.config.creator,
        publisher=archive.config.publisher,
        tags=archive.config.tags,
        main_logo_url=(
            f"{constants.download_url}/{main_logo_key}"
            if archive.config.main_logo
            else ""
        ),
        illustration_url=f"{constants.download_url}/{illus_key}",
    )
    task_id = request_task(
        project_id=project.id,
        archive_id=archive.id,
        request_def=request_def,
        email=archive.email,
    )

    # temporarily recording Archive filesize as the sum of its content
    # actual ZIM size will be updated upon completion
    archive_files_size = sum([file.filesize for file in project.files])

    # request new statis in DB (requested with the ZF ID)
    stmt = (
        update(Archive)
        .filter_by(id=archive.id)
        .values(
            filesize=archive_files_size,
            requested_on=datetime.datetime.now(tz=datetime.UTC),
            collection_json_path=collection_key,
            status=ArchiveStatus.REQUESTED,
            zimfarm_task_id=task_id,
        )
    )
    session.execute(stmt)


@router.post("/{project_id}/archives/{archive_id}/hook", status_code=HTTPStatus.CREATED)
async def record_task_feedback(
    payload: WebhookPayload,
    archive: Archive = Depends(userless_validated_archive),
    session: Session = Depends(gen_session),
    token: str = "",
    target: str = "",
):

    # we require a `token` arg equal to a setting string so we can ensure
    # hook requests are from know senders.
    # otherwises exposes us to spam abuse
    if token != constants.zimfarm_callback_token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Identify via proper token to use hook",
        )

    # discard statuses we're not interested in
    if payload.status not in ("requested", "succeeded", "failed", "canceled"):
        return {"status": "success"}

    # record task request results to DB
    stmt: ExecutableStatement | None = None
    if payload.status == "succeeded":
        try:
            if not payload.files:
                raise OSError("No files in payload")
            # should we check for file["status"] == "uploaded"?
            file: dict = next(iter(payload.files.values()))
            filesize = file["size"]
            completed_on = dateutil.parser.parse(file["uploaded_timestamp"])
            download_url = (
                f"{constants.zim_download_url}"
                f"{payload.config['warehouse_path']}/"
                f"{file['name']}"
            )
            status = ArchiveStatus.READY
        except Exception as exc:
            logger.error(f"Failed to parse callback payload: {exc!s}")
            payload.status = "failed"
        else:
            stmt = (
                update(Archive)
                .filter_by(id=archive.id)
                .values(
                    filesize=filesize,
                    completed_on=completed_on,
                    download_url=download_url,
                    status=status,
                )
            )

    if payload.status in ("failed", "canceled"):
        stmt = (
            update(Archive).filter_by(id=archive.id).values(status=ArchiveStatus.FAILED)
        )
    if stmt is not None:
        try:
            session.execute(stmt)
        except Exception as exc:
            logger.error(
                "Failed to update Archive with FAILED status {archive.id}: {exc!s}"
            )
            logger.exception(exc)

    # ensure we have a target otherwise there's no point in preparing an email
    if not target:
        return {"status": "success"}

    context = get_context(task=payload.model_dump(), archive=archive)
    subject = jinja_env.get_template("email_subject.txt").render(**context)
    body = jinja_env.get_template("email_body.html").render(**context)
    send_email_via_mailgun([target], subject, body)

    return {"status": "success"}
