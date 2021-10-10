import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker

from src.adapters.init_db import init_db
from src.adapters.orm import metadata, start_mappers
from src.services import unit_of_work


# TODO fix this approach
# engine_sqlite_memory = create_engine("sqlite:///:memory:")
# metadata.create_all(engine_sqlite_memory)
# SQLITE_SESSION_FACTORY = sessionmaker(bind=engine_sqlite_memory)


def creator():
    return sqlite3.connect("file::memory:?cache=shared", uri=True)


engine = create_engine("sqlite://", creator=creator)
metadata.create_all(engine)
SQLITE_SESSION_FACTORY = sessionmaker(bind=engine)

try:
    start_mappers()
except ArgumentError:
    pass


init_db(unit_of_work.SqlAlchemyUnitOfWork(SQLITE_SESSION_FACTORY))
