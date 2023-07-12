FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

COPY pyproject.toml README.md tasks.py /app/
COPY src/ /app/src

RUN cd /app && \
    pip install --no-cache-dir -U pip && \
    cd /app && pip install --no-cache-dir -e .[dev]

WORKDIR /app
COPY README.md /app
