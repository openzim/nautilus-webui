import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from api.constants import constants
from api.database import gen_session
from api.database.models import User

router = APIRouter(prefix="/users")


class UserModel(BaseModel):
    id: UUID
    created_on: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


@router.post("", response_model=UserModel, status_code=HTTPStatus.CREATED)
async def create_user(
    response: Response, session: Session = Depends(gen_session)
) -> UserModel:
    """Post this endpoint to create a user."""
    new_user = User(created_on=datetime.datetime.now(tz=datetime.UTC), projects=[])
    session.add(new_user)
    session.flush()
    session.refresh(new_user)
    response.set_cookie(
        key=constants.cookie_name, value=str(new_user.id), httponly=True, secure=True
    )
    return UserModel.model_validate(new_user)
