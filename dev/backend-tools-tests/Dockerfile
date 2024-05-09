FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libmagic1 redis-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY rq-worker /usr/local/bin
COPY pyproject.toml README.md tasks.py entrypoint.sh /app/
COPY api/__about__.py /app/api/
RUN chmod a+x /usr/local/bin/rq-worker \
    && cd /app \
    && chmod +x /app/entrypoint.sh \
    && pip install --no-cache-dir -U pip \
    && cd /app \
    && pip install --no-cache-dir -e .[dev]
COPY api/ /app/api
COPY tests /app/tests
COPY alembic.ini /app/alembic.ini
COPY migrations/  /app/migrations
COPY README.md /app

WORKDIR /app

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["/bin/sh"]
