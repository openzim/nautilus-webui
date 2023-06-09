import datetime
import os
import pathlib
from dataclasses import dataclass

API_VERSION_PREFIX = "/v1"

src_dir = pathlib.Path(__file__).parent.resolve()

COLLECTION_EXPIRE_AFTER = datetime.timedelta(days=7)


@dataclass
class BackendConf:
    """
    Backend configuration, read from environment variables and set default values.
    """

    database_url: str = os.getenv("POSTGRES_URI", f"sqlite:////{src_dir}/dev.sqlite")
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost|http://localhost:8000|http://localhost:8080",
    ).split("|")
