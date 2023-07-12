FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

COPY pyproject.toml README.md tasks.py /app/
COPY src/ /app/src

RUN cd /app && \
    pip install -U pip && \
    cd /app && pip install -e .[dev]

WORKDIR /app
COPY README.md /app
