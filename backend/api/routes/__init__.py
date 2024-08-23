from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.constants import constants
from api.database import gen_session
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


async def userless_validated_project(
    project_id: UUID,
    session: Session = Depends(gen_session),
) -> Project:
    """Depends()-able Project from request, ensuring it exists"""
    stmt = select(Project).filter_by(id=project_id)
    project = session.execute(stmt).scalar()
    if not project:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Project not found: {project_id}")
    return project
