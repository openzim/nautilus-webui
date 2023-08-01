FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

ENV ALLOWED_ORIGINS http://localhost
ENV POSTGRES_URI nodb

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md tasks.py entrypoint.sh /app/
COPY api/ /app/api

RUN cd /app && \
    chmod +x /app/entrypoint.sh && \
    pip install --no-cache-dir -U pip && \
    cd /app && pip install --no-cache-dir -e .

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["uvicorn", "api.entrypoint:app", "--host", "0.0.0.0", "--port", "80"]
