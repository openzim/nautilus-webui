import datetime
import logging
import os
import pathlib
from dataclasses import dataclass

API_VERSION_PREFIX = "/v1"

src_dir = pathlib.Path(__file__).parent.resolve()

PROJECT_EXPIRE_AFTER = datetime.timedelta(days=7)

logger = logging.getLogger(src_dir.name)

if not os.getenv("POSTGRES_URI"):
    msg = "Please set the POSTGRES_URI environment variable"
    raise OSError(msg)


@dataclass
class BackendConf:
    """
    Backend configuration, read from environment variables and set default values.
    """

    postgres_uri = os.getenv("POSTGRES_URI", "nodb")

    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost|http://localhost:8000|http://localhost:8080",
    ).split("|")
