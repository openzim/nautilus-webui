FROM tiangolo/uvicorn-gunicorn:python3.11-slim
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus-webui

# to set to your clients' origins
ENV ALLOWED_ORIGINS http://localhost
ENV POSTGRES_URI nodb

# internal
ENV APP_MODULE "backend.entrypoint:app"

# Set WORKDIR
WORKDIR /app

# add out prestart script launched by upstream's /start.sh and remove upstream entry
COPY prestart.sh /app/prestart.sh
RUN chmod +x /app/prestart.sh && rm -f /app/main.py

RUN pip install --no-cache-dir --upgrade pip pipenv
COPY pyproject.toml README.md tasks.py Pipfile Pipfile.lock /app/
RUN pipenv sync --system

COPY src/ /app/src
WORKDIR /app/src

# from upsteam
CMD ["/start.sh"]
