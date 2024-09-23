import datetime
from abc import ABC, abstractmethod, abstractproperty
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from api.constants import StorageType, constants
from api.database.models import File, Project


@dataclass(kw_only=True)
class StorageEntry:
    path: str
    size: int
    mimetype: str
    modified_on: datetime.datetime
    etag: str | None


class StorageInterface(ABC):

    @abstractproperty
    def storage(self): ...

    @abstractproperty
    def public_url(self) -> str: ...

    @abstractmethod
    def has(self, path: str) -> bool: ...

    @abstractmethod
    def upload_fileobj(self, fileobj: BinaryIO, path: str): ...

    @abstractmethod
    def set_autodelete_on(self, path: str, on: datetime.datetime | None): ...

    @abstractmethod
    def upload_file(self, fpath: Path, path: str): ...

    @abstractmethod
    def delete(self, path: str): ...

    @abstractmethod
    def list(self, prefix: str) -> Generator[StorageEntry, None, None]: ...

    @abstractmethod
    def mkdir(self, path: str, *, parents: bool = True, exists_ok: bool = True): ...

    @abstractmethod
    def get_file_path(self, file: File) -> str: ...

    @abstractmethod
    def get_companion_file_path(
        self, project: Project, file_hash: str, suffix: str
    ) -> str: ...


def get_storage() -> StorageInterface:
    if constants.storage_type == StorageType.WEBDAV:
        from api.storage.webdav import WebDAVStorage

        return WebDAVStorage()
    else:
        from api.storage.s3 import S3Storage

        return S3Storage()


storage = get_storage()
