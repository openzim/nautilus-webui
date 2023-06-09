from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .constants import BackendConf

engine = create_engine(BackendConf.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
