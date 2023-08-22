FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

ENV POSTGRES_URI nodb
ENV CHANNEL_NAME s3_upload
ENV REDIS_URI redis://localhost:6379/0
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md tasks.py entrypoint.sh /app/
COPY api/ /app/api
COPY alembic.ini /app/alembic.ini
COPY migrations/  /app/migrations

RUN cd /app && \
    chmod +x /app/entrypoint.sh && \
    pip install --no-cache-dir -U pip && \
    cd /app && pip install --no-cache-dir -e . 

WORKDIR /app
ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD rq worker ${CHANNEL_NAME} --url ${REDIS_URI}
