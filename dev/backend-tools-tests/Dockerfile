FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libmagic1 redis-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md tasks.py entrypoint.sh /app/
COPY api/ /app/api
COPY tests /app/tests
COPY alembic.ini /app/alembic.ini
COPY migrations/  /app/migrations

RUN cd /app && \
    chmod +x /app/entrypoint.sh && \
    pip install --no-cache-dir -U pip && \
    cd /app && pip install --no-cache-dir -e .[dev]

WORKDIR /app
COPY README.md /app

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["/bin/sh"]
