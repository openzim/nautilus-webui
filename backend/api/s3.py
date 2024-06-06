import hashlib
from uuid import UUID

from kiwixstorage import KiwixStorage

from api.constants import constants, logger


class S3Storage:
    def __init__(self) -> None:
        self._storage = None

    def _setup_s3_and_check_credentials(self, s3_url_with_credentials):
        logger.info("testing S3 Optimization Cache credentials")
        s3_storage = KiwixStorage(s3_url_with_credentials)

        if not s3_storage.check_credentials(
            list_buckets=True, bucket=True, write=True, read=True, failsafe=True
        ):
            logger.error("S3 cache connection error testing permissions.")
            logger.error(f"  Server: {s3_storage.url.netloc}")
            logger.error(f"  Bucket: {s3_storage.bucket_name}")
            logger.error(f"  Key ID: {s3_storage.params.get('keyid')}")
            raise ValueError("Unable to connect to Optimization Cache. Check its URL.")

        return s3_storage

    @property
    def storage(self):
        if not self._storage:
            self._storage = self._setup_s3_and_check_credentials(
                constants.s3_url_with_credentials
            )
        return self._storage


s3_storage = S3Storage()


def s3_file_key(project_id: UUID, file_hash: str) -> str:
    """S3 key for a Project's File"""
    digest = hashlib.sha256(
        bytes(f"{project_id}-{file_hash}-{constants.private_salt}", "utf-8")
    ).hexdigest()
    # using project_id/ pattern to ease browsing bucket for objects
    return f"{project_id}/{digest}"
