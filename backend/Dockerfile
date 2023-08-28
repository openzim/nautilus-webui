FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

ENV ALLOWED_ORIGINS http://localhost
ENV POSTGRES_URI ""
ENV PRIVATE_SALT ""
ENV S3_URL_WITH_CREDENTIALS ""
ENV REDIS_URI ""
ENV CHANNEL_NAME ""
ENV WEB_CONCURRENCY 1
ENV TRANSIENT_STORAGE_PATH /storage

VOLUME [ "/storage" ]

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md tasks.py entrypoint.sh /app/
COPY api/ /app/api
COPY alembic.ini /app/alembic.ini
COPY migrations/  /app/migrations

COPY rq-worker /usr/local/bin
RUN chmod a+x /usr/local/bin/rq-worker

RUN cd /app && \
    chmod +x /app/entrypoint.sh && \
    pip install --no-cache-dir -U pip && \
    cd /app && pip install --no-cache-dir -e . && pip install gunicorn==21.2.0

WORKDIR /app
ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["gunicorn", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind=0.0.0.0:80", \
     "--access-logfile", "-", \
     # --workers default to env WEB_CONCURRENCY or 1
     "api.entrypoint:app" \
]
