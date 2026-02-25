from pathlib import Path
from sqlalchemy.engine import Engine
from sqlalchemy import text

def init_db(engine: Engine, schema_path: str | Path | None = None) -> None:
    if schema_path is None:
        schema_path = Path(__file__).with_name("schema.sql")
    else:
        schema_path = Path(schema_path)

    sql = schema_path.read_text(encoding="utf-8")

    statements = [s.strip() for s in sql.split(";") if s.strip()]
    
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))