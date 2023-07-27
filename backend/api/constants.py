import datetime
import logging
import os
import humanfriendly
import tempfile
from dataclasses import dataclass
from pathlib import Path

API_VERSION_PREFIX = "/v1"

src_dir = Path(__file__).parent.resolve()

PROJECT_EXPIRE_AFTER = datetime.timedelta(days=7)

logger = logging.getLogger(src_dir.name)

if not os.getenv("POSTGRES_URI"):
    raise OSError("Please set the POSTGRES_URI environment variable")


@dataclass
class BackendConf:
    """
    Backend configuration, read from environment variables and set default values.
    """

    postgres_uri = os.getenv("POSTGRES_URI", "nodb")
    s3_uri = os.getenv("S3_URI")
    transient_storage_path = Path(
        os.getenv("TRANSIENT_STORAGE_PATH ", tempfile.gettempdir())
    ).resolve()

    project_quota = humanfriendly.parse_size(os.getenv("PROJECT_QUOTA", "100MiB"))
    chunk_size = humanfriendly.parse_size(os.getenv("CHUNK_SIZE", "2MiB"))

    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost|http://localhost:8000|http://localhost:8080",
    ).split("|")
