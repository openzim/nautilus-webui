import uvicorn

from api.main import create_app  # pragma: no cover

app = create_app()  # pragma: no cover


def run():
    uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    run()
