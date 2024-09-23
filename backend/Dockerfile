FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

# fully qualified URI for DB access (use postgresql+psycopg scheme)
ENV POSTGRES_URI ""
# fully qualified (Kiwix storagelib-compatible) S3 URL (use https scheme)
ENV S3_URL_WITH_CREDENTIALS ""
# a unique string used to mangle S3 keys with (so S3 keys/urls are ~private)
ENV PRIVATE_SALT ""
# fully qualified redis URL for rq-worker DB (use redis scheme)
ENV REDIS_URI ""
# a channel name to store rq-worker tasks in at redis DB
ENV CHANNEL_NAME ""
# path where files are uploaded first before being uploaded to S3
ENV TRANSIENT_STORAGE_PATH /storage
# origin URLs allowed to query the API
ENV ALLOWED_ORIGINS http://localhost
# nb of workers (subprocesses) uvicorn will start
ENV WEB_CONCURRENCY 1
# comma-separated list of IPs/networks trusted to set proper X-Forwarded-For headers
ENV FORWARDED_ALLOW_IPS "127.0.0.1"
# set any value to run database migrations on entrypoint
ENV RUN_DB_MIGRATIONS ""

VOLUME [ "/storage" ]

RUN apt-get update -y \
    && apt-get install -y libcairo2 libmagic1 libtiff5-dev libjpeg-dev libopenjp2-7-dev zlib1g-dev \
        libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev libxcb1-dev gifsicle \
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
    cd /app && pip install --no-cache-dir -e .

WORKDIR /app
ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD [ "uvicorn", \
      "--host", "0.0.0.0", \
      "--port", "80", \
      "--access-log", \
      "--log-level", "info", \
      "--proxy-headers", \
      "--no-server-header", \
      "--no-date-header", \
      "api.entrypoint:app"]
