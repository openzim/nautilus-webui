#!/bin/sh

echo "Running database migrations for ${POSTGRES_URI}…"
alembic upgrade head
exec "$@"
