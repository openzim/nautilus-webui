import datetime
import hashlib
from collections.abc import Generator
from pathlib import Path
from typing import BinaryIO

from kiwixstorage import KiwixStorage

from api.constants import constants, logger
from api.database.models import File, Project
from api.storage import StorageEntry, StorageInterface


class S3Storage(StorageInterface):
    def __init__(self) -> None:
        self._storage = None

    def _setup_s3_and_check_credentials(self, s3_url_with_credentials):
        logger.info("testing S3 Storage credentials")
        s3_storage = KiwixStorage(s3_url_with_credentials)

        if not s3_storage.check_credentials(
            list_buckets=True, bucket=True, write=True, read=True, failsafe=True
        ):
            logger.error("S3 Storage connection error testing permissions.")
            logger.error(f"  Server: {s3_storage.url.netloc}")
            logger.error(f"  Bucket: {s3_storage.bucket_name}")
            logger.error(f"  Key ID: {s3_storage.params.get('keyid')}")
            raise ValueError("Unable to connect to S3 Storage. Check its URL.")

        return s3_storage

    @property
    def storage(self):
        if not self._storage:
            self._storage = self._setup_s3_and_check_credentials(
                constants.s3_url_with_credentials
            )
        return self._storage

    @property
    def public_url(self) -> str:
        uri = self.storage.url
        query_bucket = uri.query.get("bucketName")
        # TODO: not working
        uri = (
            uri._replace(username=None)
            ._replace(password=None)
            ._replace(query=None)
            ._replace(params=None)
        )
        # we know its wasabi, use subdomain
        if query_bucket:
            if uri.hostname.endswith("wasabisys.com") and uri.hostname.startswith(
                "s3."
            ):
                uri._replace(hostname=f"{query_bucket}.{uri.hostname}")
            else:
                uri._replace(path=f"/{query_bucket}{uri.path}")
        return uri.geturl()

    def has(self, path: str) -> bool:
        return self.storage.has_object(key=path)

    def upload_fileobj(self, fileobj: BinaryIO, path: str):
        self.storage.upload_fileobj(fileobj=fileobj, key=path)

    def set_autodelete_on(self, path: str, on: datetime.datetime):
        if on is not None:
            self.storage.set_object_autodelete_on(key=path, on=on)

    def upload_file(self, fpath: Path, path: str):
        self.storage.upload_file(fpath=fpath, key=path)

    def delete(self, path: str):
        self.storage.delete_object(key=path)

    def list(self, prefix: str) -> Generator[StorageEntry, None, None]:
        for (
            summary
        ) in self.storage.resource.Bucket(  # pyright: ignore [reportAttributeAccessIssue]
            self.storage.bucket_name
        ).objects.filter(
            Prefix=prefix
        ):
            yield StorageEntry(
                path=summary.key,
                size=summary.size,
                mimetype="binary/octet-stream",
                modified_on=summary.last_modified,
                etag=summary.e_tag,
            )

    def mkdir(self, path: str, *, parents: bool = True, exists_ok: bool = True): ...

    def get_file_path(self, file: File) -> str:
        """S3 key for a Project's File"""
        digest = hashlib.sha256(
            bytes(f"{file.project_id!s}-{file.hash}-{constants.private_salt}", "utf-8")
        ).hexdigest()
        # using project_id/ pattern to ease browsing bucket for objects
        return f"{file.project_id!s}/{digest}"

    def get_companion_file_path(
        self, project: Project, file_hash: str, suffix: str
    ) -> str:
        """S3 key for a Project's companion file (not a File)"""
        # using project_id/ pattern to ease browsing bucket for objects
        return f"{project.id!s}/{file_hash}_{suffix}"
