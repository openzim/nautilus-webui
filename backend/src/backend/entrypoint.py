import uvicorn

from backend.main import create_app  # pragma: no cover

app = create_app()  # pragma: no cover

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
