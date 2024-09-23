from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, String, text, types
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.schema import MetaData
from zimscraperlib.zim.metadata import (
    validate_description,
    validate_language,
    validate_required_values,
    validate_tags,
    validate_title,
)

from api.database import get_local_fpath_for

T = TypeVar("T", bound="ArchiveConfig")


class ArchiveConfig(BaseModel):
    title: str
    description: str
    name: str
    publisher: str
    creator: str
    languages: str
    tags: list[str]
    illustration: str
    filename: str
    main_logo: str | None = None

    @classmethod
    def init_with(cls: type[T], filename: str, **kwargs) -> T:
        default = {"tags": []}
        data: dict = {key: default.get(key, "") for key in cls.model_fields.keys()}
        data.update({"filename": filename})
        if kwargs:
            data.update(kwargs)
        return cls.model_validate(data)

    def is_ready(self) -> bool:
        try:
            for key in self.model_fields.keys():
                if key != "main_logo":
                    validate_required_values(key.title(), getattr(self, key, ""))
            validate_title("Title", self.title)
            validate_description("Description", self.description)
            validate_language("Language", self.languages)
            validate_tags("Tags", self.tags)

        except ValueError:
            return False
        return True


class ArchiveStatus(str, Enum):
    # It's in database but not requested and can be modified
    PENDING = "PENDING"
    # it has been ZF-requested; can not be modified by user,
    # awaiting callback from ZimFarm
    REQUESTED = "REQUESTED"
    # ZimFarm task succeeded, it now has a download_url and filesize
    READY = "READY"
    # ZimFarm task failed, cant be downloaded
    FAILED = "FAILED"


class ArchiveConfigType(types.TypeDecorator):
    cache_ok = True
    impl = JSONB

    def process_bind_param(self, value, dialect):  # noqa: ARG002
        if isinstance(value, ArchiveConfig):
            return value.model_dump()
        if isinstance(value, dict):
            return value
        return dict(value) if value else {}

    def process_result_value(self, value, dialect) -> ArchiveConfig:  # noqa: ARG002
        if isinstance(value, ArchiveConfig):
            return value
        return ArchiveConfig.model_validate(dict(value) if value else {})

    def coerce_compared_value(self, op, value):
        return self.impl.coerce_compared_value(
            op, value
        )  # pyright: ignore [reportCallIssue]


class Base(MappedAsDataclass, DeclarativeBase):
    # This map details the specific transformation of types between Python and
    # PostgreSQL. This is only needed for the case where a specific PostgreSQL
    # type has to be used or when we want to ensure a specific setting (like the
    # timezone below)
    type_annotation_map: ClassVar = {
        ArchiveConfig: ArchiveConfigType,
        ArchiveStatus: String,
        dict[str, Any]: JSONB,  # transform Python Dict[str, Any] into PostgreSQL JSONB
        list[dict[str, Any]]: JSONB,
        datetime: DateTime(
            timezone=False
        ),  # transform Python datetime into PostgreSQL Datetime without timezone
        list[str]: ARRAY(
            item_type=String
        ),  # transform Python List[str] into PostgreSQL Array of strings
    }

    # This metadata specifies some naming conventions that will be used by
    # alembic to generate constraints names (indexes, unique constraints, ...)
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
    pass


class User(Base):
    """
    User model, used for managing users.
    """

    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(
        init=False, primary_key=True, server_default=text("uuid_generate_v4()")
    )
    created_on: Mapped[datetime]

    projects: Mapped[list["Project"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Project(Base):
    """
    Project model, used for managing projects.
    A Project is a group of files and archives.
    Project will be deleted after certain time.
    """

    __tablename__ = "project"

    id: Mapped[UUID] = mapped_column(
        init=False, primary_key=True, server_default=text("uuid_generate_v4()")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), init=False)
    name: Mapped[str]
    created_on: Mapped[datetime]
    expire_on: Mapped[datetime | None]

    user: Mapped[User] = relationship(back_populates="projects", init=False)

    webdav_path: Mapped[str | None]

    files: Mapped[list["File"]] = relationship(cascade="all, delete-orphan")
    archives: Mapped[list["Archive"]] = relationship(cascade="all, delete-orphan")

    @property
    def used_space(self):
        return sum([file.filesize for file in self.files])


class File(Base):
    """
    File model, used for managing uploaded files.
    All binary files will not be stored in the database, but in the file system.
    The files will be saved as hash values to save space.
    """

    __tablename__ = "file"

    id: Mapped[UUID] = mapped_column(
        init=False, primary_key=True, server_default=text("uuid_generate_v4()")
    )
    project_id: Mapped[UUID] = mapped_column(ForeignKey("project.id"), init=False)

    filename: Mapped[str]
    filesize: Mapped[int]
    title: Mapped[str]
    authors: Mapped[list[str] | None]
    description: Mapped[str | None]
    uploaded_on: Mapped[datetime]
    hash: Mapped[str]
    path: Mapped[str]
    type: Mapped[str]
    status: Mapped[str]

    @property
    def local_fpath(self):
        return get_local_fpath_for(self.hash, self.project_id)


class Archive(Base):
    """
    Archive model, used for managing archives.
    Arhcives are zim files and will be generated by zimfarm.
    All of the archives will be deleted after certain time.
    """

    __tablename__ = "archive"

    id: Mapped[UUID] = mapped_column(
        init=False, primary_key=True, server_default=text("uuid_generate_v4()")
    )
    project_id: Mapped[UUID] = mapped_column(ForeignKey("project.id"), init=False)

    filesize: Mapped[int | None]
    created_on: Mapped[datetime]
    requested_on: Mapped[datetime | None]
    completed_on: Mapped[datetime | None]
    download_url: Mapped[str | None]
    collection_json_path: Mapped[str | None]
    status: Mapped[ArchiveStatus]
    zimfarm_task_id: Mapped[UUID | None]
    email: Mapped[str | None]
    config: Mapped[ArchiveConfig]
