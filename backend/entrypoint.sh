#!/bin/sh

if [ "$RUN_DB_MIGRATIONS" != "" ];
then
	echo "Running database migrations for ${POSTGRES_URI}…"
	alembic upgrade head
fi
exec "$@"
