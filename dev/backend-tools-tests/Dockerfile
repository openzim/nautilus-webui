FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip pipenv
COPY pyproject.toml README.md tasks.py Pipfile Pipfile.lock /app/
RUN pipenv sync --system

COPY src/ /app/src
COPY README.md /app
