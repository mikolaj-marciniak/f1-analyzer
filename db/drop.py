from sqlalchemy.engine import Engine

def drop_db(engine: Engine) -> None:
    sql = "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

    with engine.begin() as conn:
        raw = conn.connection
        with raw.cursor() as cur:
            cur.execute(sql)