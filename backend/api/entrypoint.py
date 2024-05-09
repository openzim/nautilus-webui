import sys

import uvicorn

from api.main import create_app  # pragma: no cover
from api.s3 import s3_storage

# dont check S3 credentials URL in tests
if "pytest" not in sys.modules:
    # raises should S3 credentials URL be malformed
    _ = s3_storage.storage
app = create_app()  # pragma: no cover


def run():
    uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    run()
