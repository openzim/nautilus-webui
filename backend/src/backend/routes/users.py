import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from httpx import codes
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.database import gen_session
from backend.database.models import User

router = APIRouter(prefix="/users")


class UserModel(BaseModel):
    id: UUID
    created_on: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


@router.post("", response_model=UserModel, status_code=codes.CREATED)
async def create_user(
    response: Response, session: Session = Depends(gen_session)
) -> UserModel:
    """Post this endpoint to create a user."""
    new_user = User(created_on=datetime.datetime.now(tz=datetime.UTC), projects=[])
    session.add(new_user)
    session.flush()
    session.refresh(new_user)
    response.set_cookie(key="user_id", value=str(new_user.id))
    return UserModel.model_validate(new_user)
