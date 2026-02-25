from sqlalchemy.engine import Engine

from db.engine import get_engine
from db.init_db import init_db

def run(season: int, engine: Engine | None = None) -> None:
    if engine is None:
        engine = get_engine()

    init_db(engine)

if __name__ == "__main__":
    run(2024)