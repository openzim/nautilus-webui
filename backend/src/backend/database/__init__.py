from typing import Generator

from bson.json_util import DEFAULT_JSON_OPTIONS, dumps, loads
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.orm import sessionmaker

from backend.constants import BackendConf, logger


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


if (
    BackendConf.postgres_uri == "nodb"
):  # this is a hack for cases where we do not need the DB, e.g. unit tests
    Session = None
else:
    Session = sessionmaker(
        bind=create_engine(
            BackendConf.postgres_uri,
            echo=False,
            json_serializer=dumps,  # use bson serializer to handle datetime naively
            json_deserializer=my_loads,  # use custom bson deserializer for same reason
        )
    )


def gen_session() -> Generator[OrmSession, None, None]:
    """FastAPI's Depends() compatible helper to provide a began DB Session"""
    with Session.begin() as session:
        try:
            yield session
        except Exception as exc:
            logger.exception(exc)
            session.rollback()
