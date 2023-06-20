from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from httpx import codes
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import gen_session
from backend.database.models import User

router = APIRouter()

PREFIX = "/user"


class UserModel(BaseModel):
    id: UUID
    created_on: datetime

    class Config:
        orm_mode = True


@router.post(PREFIX, response_model=UserModel, status_code=codes.CREATED)
async def create_user(session: Session = Depends(gen_session)) -> UserModel:
    """Post this endpoint to create a user."""
    new_user = User(created_on=datetime.utcnow())
    session.add(new_user)
    session.flush()
    session.refresh(new_user)
    return UserModel.from_orm(new_user)
