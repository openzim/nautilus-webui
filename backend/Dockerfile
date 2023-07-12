FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

ENV ALLOWED_ORIGINS http://localhost
ENV POSTGRES_URI nodb

COPY pyproject.toml README.md tasks.py entrypoint.sh /app/
COPY src/ /app/src

RUN cd /app && \
    chmod +x /app/entrypoint.sh && \
    pip install --no-cache-dir -U pip && \
    cd /app && pip install --no-cache-dir -e .

WORKDIR /app/src

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["uvicorn", "backend.entrypoint:app", "--host", "0.0.0.0", "--port", "80"]
