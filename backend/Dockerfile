FROM python:3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

ENV ALLOWED_ORIGINS http://localhost
ENV POSTGRES_URI nodb
ENV ALLOWED_ORIGINS http://localhost

COPY pyproject.toml README.md tasks.py entrypoint.sh Pipfile Pipfile.lock /app/
RUN pip install --no-cache-dir pip pipenv && \
    chmod +x /app/entrypoint.sh && \
    cd /app && \
    pipenv sync --system
COPY src/ /app/src
WORKDIR /app/src

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["uvicorn", "backend.entrypoint:app", "--host", "0.0.0.0", "--port", "80"]
