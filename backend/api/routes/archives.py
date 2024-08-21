import base64
import datetime
import io
import json
from http import HTTPStatus
from typing import Any, BinaryIO
from uuid import UUID

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
from api.routes import validated_project
from api.s3 import s3_file_key, s3_storage
from api.zimfarm import RequestSchema, WebhookPayload, request_task

router = APIRouter()


class ArchiveRequest(BaseModel):
    email: str | None
    config: ArchiveConfig

    model_config = ConfigDict(from_attributes=True)


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
                "uri": f"{constants.download_url}/{s3_file_key(project.id, file.hash)}",
                "filename": file.filename,
            }
        ]
        collection.append(entry)

    file = io.BytesIO()
    file.write(json.dumps(collection, indent=2, ensure_ascii=False).encode("UTF-8"))
    file.seek(0)

    digest = generate_file_hash(file)

    return collection, file, digest


def get_collection_key(project_id: UUID, collection_hash: str) -> str:
    # using .json suffix (for now) so we can debug live URLs in-browser
    return f"{s3_file_key(project_id=project_id, file_hash=collection_hash)}.json"


def upload_collection_to_s3(project: Project, collection_file: BinaryIO, s3_key: str):

    try:
        if s3_storage.storage.has_object(s3_key):
            logger.debug(f"Object `{s3_key}` already in S3… weird but OK")
            return
        logger.debug(f"Uploading collection to `{s3_key}`")
        s3_storage.storage.upload_fileobj(fileobj=collection_file, key=s3_key)
        s3_storage.storage.set_object_autodelete_on(s3_key, project.expire_on)
    except Exception as exc:
        logger.error(f"Collection failed to upload to s3 `{s3_key}`: {exc}")
        raise exc


@router.post(
    "/{project_id}/archives/{archive_id}/request", status_code=HTTPStatus.CREATED
)
async def request_archive(
    archive: Archive = Depends(validated_archive),
    project: Project = Depends(validated_project),
    session: Session = Depends(gen_session),
):
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

    # gen collection and stream
    collection, collection_file, collection_hash = gen_collection_for(project=project)
    collection_key = get_collection_key(
        project_id=archive.project_id, collection_hash=collection_hash
    )

    # upload it to S3
    upload_collection_to_s3(
        project=project,
        collection_file=collection_file,
        s3_key=collection_key,
    )

    # Everything's on S3, prepare and submit a ZF request
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
        main_logo_url=None,
        illustration_url=f"{constants.download_url}/{collection_key}",
    )
    task_id = request_task(
        archive_id=archive.id, request_def=request_def, email=archive.email
    )

    # request new statis in DB (requested with the ZF ID)
    stmt = (
        update(Archive)
        .filter_by(id=archive.id)
        .values(
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
    archive: Archive = Depends(validated_archive),
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
            # should we check for file["status"] == "uploaded"?
            file: dict = next(iter(payload.files.values()))
            filesize = file["size"]
            completed_on = datetime.datetime.fromisoformat(file["uploaded_timestamp"])
            download_url = (
                f"{constants.download_url}/"
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
            session.commit()
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
    send_email_via_mailgun(target, subject, body)

    return {"status": "success"}
