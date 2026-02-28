import pandas as pd
from sqlalchemy import text
from db.engine import get_engine

def get_seasons() -> pd.DataFrame:
    sql = text(f"""
        SELECT season
        FROM race
        GROUP BY season
        ORDER BY season ASC;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn)