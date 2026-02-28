import pandas as pd
from sqlalchemy import text
from db.engine import get_engine

def get_drivers(ascending: bool = True) -> pd.DataFrame:
    order = "ASC" if ascending else "DESC"

    sql = text(f"""
        SELECT _id, family_name, name
        FROM driver
        ORDER BY family_name {order}, name {order};
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn)
    
def get_driver_data(driver_id: int) -> pd.DataFrame:
    sql = text("""
        SELECT _id, name, family_name, date_of_birth, nationality
        FROM driver
        WHERE _id = :driver_id;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'driver_id': driver_id})

def get_best_circuit_of_driver(driver_id: int) -> pd.DataFrame:
    sql = text("""
        SELECT c.name, c.location, c.country, AVG(res.position::numeric) as mean_pos
        FROM result res
        JOIN race r    ON res.fk_race_id = r._id
        JOIN circuit c ON r.fk_circuit_id = c._id
        WHERE res.fk_driver_id = :driver_id
            AND res.position IS NOT NULL
        GROUP BY c._id, c.name, c.location, c.country
        ORDER BY mean_pos ASC
        LIMIT 1;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'driver_id': driver_id})

def get_most_gained_positions_by_driver(driver_id: int) -> pd.DataFrame:
    sql = text("""
        SELECT (res.grid - res.position) diff
        FROM result res
        WHERE res.fk_driver_id = :driver_id
            AND res.grid IS NOT NULL
            AND res.position IS NOT NULL
        ORDER BY diff DESC
        LIMIT 1;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'driver_id': driver_id})