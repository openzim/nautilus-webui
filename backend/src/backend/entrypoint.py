import uvicorn

from backend.main import create_app  # pragma: no cover

app = create_app()  # pragma: no cover

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
