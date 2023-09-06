import datetime
import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

import humanfriendly
from rq import Retry


def determine_mandatory_environment_variables():
    for variable in ("POSTGRES_URI", "S3_URL_WITH_CREDENTIALS", "PRIVATE_SALT"):
        if not os.getenv(variable):
            raise OSError(f"Please set the {variable} environment variable")


@dataclass(kw_only=True)
class BackendConf:
    """
    Backend configuration, read from environment variables and set default values.
    """

    logger: logging.Logger = field(init=False)

    # Mandatory configurations
    postgres_uri = os.getenv("POSTGRES_URI", "nodb")
    s3_url_with_credentials = os.getenv("S3_URL_WITH_CREDENTIALS")
    private_salt = os.getenv("PRIVATE_SALT")

    # Optional configuration.
    s3_max_tries = int(os.getenv("S3_MAX_TRIES", "3"))
    s3_retry_wait = humanfriendly.parse_timespan(os.getenv("S3_RETRY_TIMES", "10s"))
    s3_deletion_delay = datetime.timedelta(
        hours=int(os.getenv("S3_REMOVE_DELETEDUPLOADING_AFTER_HOURS", "12"))
    )
    transient_storage_path = Path(
        os.getenv("TRANSIENT_STORAGE_PATH", tempfile.gettempdir())
    ).resolve()
    redis_uri = os.getenv("REDIS_URI", "redis://localhost:6379/0")
    channel_name = os.getenv("CHANNEL_NAME", "s3_upload")
    cookie_domain = os.getenv("COOKIE_DOMAIN", None)
    cookie_expiration_days = int(os.getenv("COOKIE_EXPIRATION_DAYS", "30"))
    project_quota = humanfriendly.parse_size(os.getenv("PROJECT_QUOTA", "100MB"))
    chunk_size = humanfriendly.parse_size(os.getenv("CHUNK_SIZE", "2MiB"))
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost",
    ).split("|")

    authentication_cookie_name: str = "user_id"
    api_version_prefix = "/v1"
    project_expire_after = datetime.timedelta(days=7)
    empty_uuid = UUID("263acb5d-d6ca-4e12-92a4-94d4f59fa18b")

    def __post_init__(self):
        self.logger = logging.getLogger(Path(__file__).parent.name)
        self.transient_storage_path.mkdir(exist_ok=True)
        self.job_retry = Retry(max=self.s3_max_tries, interval=int(self.s3_retry_wait))


constants = BackendConf()
logger = constants.logger
