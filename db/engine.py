import os
from dotenv import load_dotenv
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine

load_dotenv()

def get_engine() -> Engine:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("Brak DATABASE_URL w .env")
    return create_engine(db_url, pool_pre_ping=True)