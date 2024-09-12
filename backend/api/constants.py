import datetime
import logging
import os
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

import humanfriendly
from rq import Retry

logging.basicConfig()


def determine_mandatory_environment_variables():
    for variable in ("POSTGRES_URI", "S3_URL_WITH_CREDENTIALS", "PRIVATE_SALT"):
        if not os.getenv(variable):
            raise OSError(f"Please set the {variable} environment variable")


@dataclass(kw_only=True)
class BackendConf:
    """
    Backend configuration, read from environment variables and set default values.
    """

    # Configuration
    project_expire_after: datetime.timedelta = datetime.timedelta(days=7)
    project_quota: int = 0
    chunk_size: int = 1024  # reading/writing received files
    illustration_quota: int = 0
    api_version_prefix: str = "/v1"  # our API

    # single-user mode (Kiwix only)
    single_user_id: str = os.getenv("SINGLE_USER_ID", "").strip() or ""

    # Database
    postgres_uri: str = os.getenv("POSTGRES_URI") or "nodb"

    # Scheduler process
    redis_uri: str = os.getenv("REDIS_URI") or "redis://localhost:6379/0"
    channel_name: str = os.getenv("CHANNEL_NAME") or "s3_upload"

    # Transient (on host disk) Storage
    transient_storage_path: Path = Path()

    # S3 Storage
    s3_url_with_credentials: str = os.getenv("S3_URL_WITH_CREDENTIALS") or ""
    s3_max_tries: int = int(os.getenv("S3_MAX_TRIES", "3"))
    s3_retry_wait: int = int(
        humanfriendly.parse_timespan(os.getenv("S3_RETRY_TIMES") or "10s")
    )
    s3_deletion_delay: datetime.timedelta = datetime.timedelta(
        hours=int(os.getenv("S3_REMOVE_DELETEDUPLOADING_AFTER_HOURS", "12"))
    )
    private_salt = os.getenv(
        "PRIVATE_SALT", uuid.uuid4().hex
    )  # used to make S3 keys unguessable

    # Cookies
    cookie_domain = os.getenv("COOKIE_DOMAIN", None)
    cookie_expiration_days = int(os.getenv("COOKIE_EXPIRATION_DAYS", "30"))
    authentication_cookie_name: str = "user_id"

    # Deployment
    public_url: str = os.getenv("PUBLIC_URL") or "http://localhost"
    # /!\ this must match the region/bucket on s3 credentials
    download_url: str = (
        os.getenv("DOWNLOAD_URL")
        or "https://s3.eu-west-2.wasabisys.com/org-kiwix-nautilus"
    )
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost",
    ).split("|")
    debug: bool = bool(os.getenv("DEBUG") or "")

    # Zimfarm (3rd party API creating ZIMs and calling back with feedback)
    zimfarm_api_url: str = (
        os.getenv("ZIMFARM_API_URL") or "https://api.farm.zimit.kiwix.org/v1"
    )
    zimfarm_username: str = os.getenv("ZIMFARM_API_USERNAME") or ""
    zimfarm_password: str = os.getenv("ZIMFARM_API_PASSWORD") or ""
    zimfarm_nautilus_image: str = (
        os.getenv("ZIMFARM_NAUTILUS_IMAGE") or "ghcr.io/openzim/nautilus:latest"
    )
    zimfarm_task_cpu: int = int(os.getenv("ZIMFARM_TASK_CPU") or "3")
    zimfarm_task_memory: int = 0
    zimfarm_task_disk: int = 0
    zimfarm_callback_base_url = (
        os.getenv("ZIMFARM_CALLBACK_BASE_URL") or "https://api.nautilus.openzim.org/v1"
    )
    zimfarm_callback_token = os.getenv("ZIMFARM_CALLBACK_TOKEN", uuid.uuid4().hex)
    zimfarm_task_worker: str = os.getenv("ZIMFARM_TASK_WORKER") or "-"
    zimfarm_request_timeout_sec: int = 10
    zim_download_url: str = (
        os.getenv("ZIM_DOWNLOAD_URL")
        or "https://s3.us-west-1.wasabisys.com/org-kiwix-zimit"
    )

    # Mailgun (3rd party API to send emails)
    mailgun_api_url: str = os.getenv("MAILGUN_API_URL") or ""
    mailgun_api_key: str = os.getenv("MAILGUN_API_KEY") or ""
    mailgun_from: str = os.getenv("MAILGUN_FROM") or "Nautilus ZIM"
    mailgun_request_timeout_sec: int = 10

    logger: logging.Logger = field(init=False)

    def __post_init__(self):
        self.logger = logging.getLogger(Path(__file__).parent.name)
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        self.transient_storage_path.mkdir(exist_ok=True)
        self.job_retry = Retry(max=self.s3_max_tries, interval=int(self.s3_retry_wait))

        self.transient_storage_path = Path(
            os.getenv("TRANSIENT_STORAGE_PATH") or tempfile.gettempdir()
        ).resolve()

        self.project_quota = humanfriendly.parse_size(
            os.getenv("PROJECT_QUOTA") or "100MB"
        )

        self.chunk_size = humanfriendly.parse_size(os.getenv("CHUNK_SIZE", "2MiB"))

        self.illustration_quota = humanfriendly.parse_size(
            os.getenv("ILLUSTRATION_QUOTA", "2MiB")
        )

        self.zimfarm_task_memory = humanfriendly.parse_size(
            os.getenv("ZIMFARM_TASK_MEMORY") or "1000MiB"
        )
        self.zimfarm_task_disk = humanfriendly.parse_size(
            os.getenv("ZIMFARM_TASK_DISK") or "200MiB"
        )

    @property
    def single_user(self) -> UUID:
        return UUID(self.single_user_id)


constants = BackendConf()
logger = constants.logger
