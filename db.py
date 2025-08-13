from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel


def get_engine() -> Engine:
    sqlite_filename = "database.db"
    sqlite_url = f"sqlite:///{sqlite_filename}"

    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    engine.connect()
    return engine


def create_db_and_tables(engine: Engine):
    SQLModel.metadata.create_all(engine)


