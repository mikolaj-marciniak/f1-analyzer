import pandas as pd

from sqlalchemy.engine import Engine
from sqlalchemy import text

def get_last_loaded_season(engine: Engine) -> int | None:
    sql = text("""
        SELECT MAX(r.season) as season
        FROM result res
        LEFT JOIN race r ON res.fk_race_id = r._id
    """)

    with engine.begin() as conn:
        dataframe = pd.read_sql(sql, conn)

    val = dataframe.loc[0, 'season']

    if pd.isna(val):
        return None
    return int(val)