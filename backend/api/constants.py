import datetime
import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import humanfriendly

if not os.getenv("POSTGRES_URI"):
    raise OSError("Please set the POSTGRES_URI environment variable")


@dataclass(kw_only=True)
class BackendConf:
    """
    Backend configuration, read from environment variables and set default values.
    """

    logger: logging.Logger = field(init=False)

    postgres_uri = os.getenv("POSTGRES_URI", "nodb")
    s3_uri = os.getenv("S3_URI")
    transient_storage_path = Path(
        os.getenv("TRANSIENT_STORAGE_PATH ", tempfile.gettempdir())
    ).resolve()

    authentication_cookie_name: str = "user_id"
    cookie_domain = os.getenv("COOKIE_DOMAIN", None)
    cookie_expiration_days = int(os.getenv("COOKIE_EXPIRATION_DAYS", "30"))
    api_version_prefix = "/v1"
    project_expire_after = datetime.timedelta(days=7)
    project_quota = humanfriendly.parse_size(os.getenv("PROJECT_QUOTA", "100MiB"))

    chunk_size = humanfriendly.parse_size(os.getenv("CHUNK_SIZE", "2MiB"))

    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost",
    ).split("|")

    def __post_init__(self):
        self.logger = logging.getLogger(Path(__file__).parent.name)
        self.transient_storage_path.mkdir(exist_ok=True)


constants = BackendConf()
logger = constants.logger
