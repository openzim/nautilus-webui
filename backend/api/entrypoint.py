import sys

import uvicorn

from api import storage
from api.main import create_app  # pragma: no cover

# dont check S3 credentials URL in tests
if "pytest" not in sys.modules:
    # raises should S3 credentials URL be malformed (attempts to use)
    _ = storage.storage
app = create_app()  # pragma: no cover


def run():
    uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    run()
