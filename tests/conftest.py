import os
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.db import Base  # noqa: E402


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine("sqlite:///:memory:", future=True)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    tables = [
        t for name, t in Base.metadata.tables.items() if name != "knowledge_docs"
    ]
    Base.metadata.create_all(bind=engine, tables=tables)

    yield TestingSession

    Base.metadata.drop_all(bind=engine, tables=tables)


@pytest.fixture()
def ticket_id():
    return str(uuid.uuid4())