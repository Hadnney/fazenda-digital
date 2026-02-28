from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///fazenda.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

from sqlalchemy import inspect

# Auto-initialize database if tables are missing, works globally for all pages
inspector = inspect(engine)
if not inspector.has_table("animals"):
    # Local import to avoid circular dependency
    from init_db import init_db
    init_db()


def get_db():
    """
    Deprecated: usage with next(get_db()) is unsafe in Streamlit.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
