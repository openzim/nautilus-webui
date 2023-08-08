from collections.abc import Generator
from uuid import UUID

from bson.json_util import DEFAULT_JSON_OPTIONS, dumps, loads
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.orm import sessionmaker

from api.constants import constants, logger


# custom overload of bson deserializer to make naive datetime
# this is needed to have objects from the DB with naive datetime properties
# (otherwise the deserialization produces aware datetimes based on local TZ)
def my_loads(s, *args, **kwargs):
    return loads(
        s,
        *args,
        json_options=DEFAULT_JSON_OPTIONS.with_options(tz_aware=False, tzinfo=None),
        **kwargs,
    )


Session = sessionmaker(
    bind=create_engine(
        constants.postgres_uri,
        echo=False,
        json_serializer=dumps,  # use bson serializer to handle datetime naively
        json_deserializer=my_loads,  # use custom bson deserializer for same reason
    )
)


def gen_session() -> Generator[OrmSession, None, None]:
    """FastAPI's Depends() compatible helper to provide a began DB Session"""
    with Session.begin() as session:
        yield session


def get_local_fpath_for(file_hash: str, project_id: UUID):
    """Generates the local file path for a given file hash and project ID."""
    return constants.transient_storage_path.joinpath(f"{project_id}-{file_hash}")
