import uuid
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from sqlalchemy_utils import EmailType, JSONType, UUIDType

from backend.constants import COLLECTION_EXPIRE_TIME

from .database import Base


class User(Base):
    """
    User model, used for managing users.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False, default=""
    )
    created_on = mapped_column(DateTime(timezone=True), default=datetime.utcnow())

    collections: Mapped[List["Collection"]] = relationship()


class Collection(Base):
    """
    Collection model, used for managing collections.
    A collection is a group of files and archives.
    collection will be deleted after certain time.
    """

    __tablename__ = "collections"

    id: Mapped[UUID] = mapped_column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String, nullable=False, default="")
    email = mapped_column(EmailType)
    created_on = mapped_column(DateTime(timezone=True), server_default=func.now())
    expire_on = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow() + timedelta(days=COLLECTION_EXPIRE_TIME),
    )

    files: Mapped[List["File"]] = relationship()
    archives: Mapped[List["Archive"]] = relationship()


class File(Base):
    """
    File model, used for managing uploaded files.
    All binary files will not be stored in the database, but in the file system.
    The files will be saved as hash values to save space.
    """

    __tablename__ = "files"

    id: Mapped[UUID] = mapped_column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4, index=True
    )
    collection_id: Mapped[UUID] = mapped_column(ForeignKey("collections.id"))

    filename: Mapped[str] = mapped_column(String, nullable=False, default="")
    title: Mapped[str] = mapped_column(String, nullable=False, default="")
    authors: Mapped[str] = mapped_column(String, nullable=False, default="")
    hash: Mapped[str] = mapped_column(String, nullable=False, default="")
    path: Mapped[str] = mapped_column(String, nullable=False, default="")
    type: Mapped[str] = mapped_column(String, nullable=False, default="")


class Archive(Base):
    """
    Archive model, used for managing archives.
    Arhcives are zim files and will be generated by zimfarm.
    All of the archives will be deleted after certain time.
    """

    __tablename__ = "archives"

    id: Mapped[UUID] = mapped_column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4, index=True
    )
    collection_id: Mapped[UUID] = mapped_column(ForeignKey("collections.id"))

    filename: Mapped[str] = mapped_column(String, nullable=False, default="")
    created_on = mapped_column(DateTime(timezone=True))
    requested_on = mapped_column(DateTime(timezone=True))
    download_url: Mapped[str] = mapped_column(String, nullable=False, default="")
    collection_json_path: Mapped[str] = mapped_column(
        String, nullable=False, default=""
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="")
    zimfarm_task_id: Mapped[str] = mapped_column(String, nullable=False, default="")
    config: Mapped[JSON] = mapped_column(JSONType, nullable=False)
