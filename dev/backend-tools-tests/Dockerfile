FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md tasks.py /app/
COPY api/ /app/api
COPY alembic.ini /app/alembic.ini
COPY migrations/  /app/migrations

RUN cd /app && \
    pip install --no-cache-dir -U pip && \
    cd /app && pip install --no-cache-dir -e .[dev]

WORKDIR /app
COPY README.md /app
