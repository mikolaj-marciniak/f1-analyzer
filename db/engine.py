import os
from dotenv import load_dotenv

from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

def get_engine() -> Engine:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("Brak DATABASE_URL w .env")
    return create_engine(db_url, pool_pre_ping=True)

def check_connection(engine: Engine) -> None:
    try:
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        raise RuntimeError(f"Nie mogę połączyć się z bazą. Sprawdź DATABASE_URL. Szczegóły: {e}") from e