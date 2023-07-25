import datetime
import logging
import os
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
    temp_files_location = Path(
        os.getenv("TEMP_FILES_LOCATION", tempfile.gettempdir())
    ).resolve()

    maximum_upload_file_size = int(os.getenv("MAXIMUM_UPLOAD_FILE_SIZE", "104857600"))

    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost|http://localhost:8000|http://localhost:8080",
    ).split("|")
