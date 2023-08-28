from kiwixstorage import KiwixStorage

from api.constants import constants, logger


class S3Storage:
    def __init__(self) -> None:
        self._storage = None

    def _setup_s3_and_check_credentials(self, s3_url_with_credentials):
        logger.info("testing S3 Optimization Cache credentials")
        s3_storage = KiwixStorage(s3_url_with_credentials)
        # We Don't check read and write permissions here,
        # See: https://github.com/openzim/python-storagelib/issues/11
        if not s3_storage.check_credentials(
            list_buckets=True, bucket=True, failsafe=True
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
