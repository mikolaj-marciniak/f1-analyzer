from pathlib import Path

from sqlalchemy.engine import Engine

def init_db(engine: Engine, schema_path: str | Path | None = None) -> None:
    if schema_path is None:
        schema_path = Path(__file__).with_name("schema.sql")
    else:
        schema_path = Path(schema_path)

    if not schema_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku schema.sql: {schema_path}")

    sql = schema_path.read_text(encoding="utf-8")
    
    with engine.begin() as conn:
        raw = conn.connection
        with raw.cursor() as cur:
            cur.execute(sql)