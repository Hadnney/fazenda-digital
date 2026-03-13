from contextlib import contextmanager
from sqlalchemy import create_engine, text
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

# --- Migração automática: adiciona colunas do ciclo produtivo se não existirem ---
_MIGRACOES = [
    ("fase",              "ALTER TABLE animals ADD COLUMN fase TEXT DEFAULT 'cria'"),
    ("data_fase",         "ALTER TABLE animals ADD COLUMN data_fase TEXT"),
    ("peso_entrada_fase", "ALTER TABLE animals ADD COLUMN peso_entrada_fase REAL"),
]

with engine.connect() as _conn:
    _cols_existentes = {c["name"] for c in inspect(engine).get_columns("animals")}
    for _col, _sql in _MIGRACOES:
        if _col not in _cols_existentes:
            try:
                _conn.execute(text(_sql))
                _conn.commit()
            except Exception:
                pass  # coluna já existe ou outro erro não-crítico


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
