import datetime
import mimetypes
from collections.abc import Generator
from pathlib import Path
from typing import BinaryIO
from urllib.parse import ParseResult, urlparse

from webdav4.client import Client as DAVClient
from webdav4.client import ResourceAlreadyExists

from api.constants import constants, logger
from api.database.models import File, Project
from api.database.utils import get_project_by_id
from api.storage import StorageEntry, StorageInterface


class WebDAVUrl:
    _uri: ParseResult

    def __init__(self, webdav_url_with_credentials: str):
        self._uri = urlparse(webdav_url_with_credentials)

    @property
    def public_url(self) -> str:
        port_suffix = f":{self._uri.port}" if self._uri.port else ""
        return self._uri._replace(netloc=f"{self._uri.hostname}{port_suffix}").geturl()

    @property
    def auth(self) -> tuple[str, str] | None:
        return (
            None
            if not self._uri.username
            else (self._uri.username or "", self._uri.password or "")
        )

    @property
    def path(self) -> str:
        return self._uri.path


class WebDAVStorage(StorageInterface):
    def __init__(self) -> None:
        self._storage = None

    def _setup_webdav_and_check_credentials(self, webdav_url_with_credentials):
        logger.info("testing WebDAV credentials")
        try:
            public_url, auth = explode_webdav_credentials(webdav_url_with_credentials)

            dav_url = WebDAVUrl(webdav_url_with_credentials)
            client = DAVClient(
                dav_url.public_url,
                auth=dav_url.auth,
                timeout=constants.webdav_request_timeout_sec,
            )
            client.ls(dav_url.path)
        except Exception as exc:
            logger.error(f"WebDAV error: {exc!s}")
            raise ValueError("Unable to connect to WebDAV. Check its URL.") from exc

        return client

    @property
    def storage(self):
        if not self._storage:
            self._storage = self._setup_webdav_and_check_credentials(
                constants.webdav_url_with_credentials
            )
        return self._storage

    @property
    def public_url(self) -> str:
        return str(self.storage.base_url)

    def has(self, path: str) -> bool:
        return self.storage.exists(path)

    def upload_fileobj(self, fileobj: BinaryIO, path: str):
        self.storage.upload_fileobj(file_obj=fileobj, to_path=path, overwrite=True)

    def set_autodelete_on(
        self, path: str, on: datetime.datetime | None  # noqa: ARG002
    ):
        logger.warning(
            f"requested autodelete for {path} while storage doesnt support it"
        )

    def upload_file(self, fpath: Path, path: str):
        self.storage.upload_file(from_path=fpath, to_path=path, overwrite=True)

    def delete(self, path: str):
        self.storage.remove(path)

    def list(self, prefix: str) -> Generator[StorageEntry, None, None]:
        for entry in self.storage.ls(prefix, detail=True, allow_listing_resource=True):
            # we should not get there (detail=True) but type checker doesnt know
            if not isinstance(entry, dict):
                continue
            if entry["type"] == "directory":
                yield from self.list(entry["name"])
            # we only want files
            if entry["type"] != "file":
                continue
            if not isinstance(entry, dict):
                continue
            fpath = Path(entry["name"])
            if "__MACOSX" in fpath.parts:
                continue
            if "DS_Store" in fpath.parts:
                continue
            yield StorageEntry(
                path=entry["name"],
                size=entry["content_length"],
                mimetype=entry["content_type"]
                or mimetypes.types_map.get(fpath.suffix)
                or "binary/octet-stream",
                modified_on=entry["modified"],
                etag=entry["etag"],
            )

    def mkdir(self, path: str, *, parents: bool = True, exists_ok: bool = True):
        ppath = Path(path)
        if parents:
            for parent in list(reversed(ppath.parents))[1:]:
                try:
                    self.storage.mkdir(path=str(parent))
                except ResourceAlreadyExists:
                    ...
        try:
            self.storage.mkdir(path)
        except ResourceAlreadyExists as exc:
            if not exists_ok:
                raise exc

    def get_file_path(self, file: File) -> str:
        """WebDAV path for a Project's File"""
        project = get_project_by_id(file.project_id)
        if project.webdav_path is None:
            raise ValueError("project unconfigured: no webdav_path")
        return f"{project.webdav_path}/{file.filename}"

    def get_companion_file_path(
        self, project: Project, file_hash: str, suffix: str  # noqa: ARG002
    ) -> str:
        """S3 key for a Project's companion file (not a File)"""
        # using project_id/ pattern to ease browsing bucket for objects
        if project.webdav_path is None:
            raise ValueError("project unconfigured: no webdav_path")
        return f"{project.webdav_path!s}/{suffix}"


def explode_webdav_credentials(url: str) -> tuple[str, tuple[str, str] | None]:
    """ """
    uri = urlparse(url)
    port_suffix = f":{uri.port}" if uri.port else ""
    auth = None if not uri.username else (uri.username or "", uri.password or "")
    public = uri._replace(netloc=f"{uri.hostname}{port_suffix}").geturl()
    return public, auth
