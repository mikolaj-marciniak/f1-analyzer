import pandas as pd
from sqlalchemy import text
from db.engine import get_engine

def get_circuits(ascending: bool = True) -> pd.DataFrame:
    order = "ASC" if ascending else "DESC"

    sql = text(f"""
        SELECT _id, name
        FROM circuit
        ORDER BY name {order};
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn)
    
def get_circuit_data(circuit_id: int) -> pd.DataFrame:
    sql = text("""
        SELECT _id, name, location, country
        FROM circuit
        WHERE _id = :circuit_id;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'circuit_id': circuit_id})

def get_best_driver_on_circuit(circuit_id: int) -> pd.DataFrame:
    sql = text("""
        SELECT d.name, d.family_name, AVG(res.position::numeric) as mean_pos
        FROM result res
        JOIN driver d  ON res.fk_driver_id = d._id
        JOIN race r    ON res.fk_race_id = r._id
        WHERE r.fk_circuit_id = :circuit_id
            AND res.position IS NOT NULL
        GROUP BY d._id, d.name, d.family_name
        ORDER BY mean_pos ASC
        LIMIT 1;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'circuit_id': circuit_id})

def get_best_team_on_circuit(circuit_id: int) -> pd.DataFrame:
    sql = text("""
        SELECT t.name, AVG(res.position::numeric) as mean_pos
        FROM result res
        JOIN team t  ON res.fk_team_id = t._id
        JOIN race r    ON res.fk_race_id = r._id
        WHERE r.fk_circuit_id = :circuit_id
            AND res.position IS NOT NULL
        GROUP BY t._id, t.name
        ORDER BY mean_pos ASC
        LIMIT 1;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'circuit_id': circuit_id})

def get_most_gained_positions_on_circuit(circuit_id: int) -> pd.DataFrame:
    sql = text("""
        SELECT d.name, d.family_name, (res.grid - res.position) diff
        FROM result res
        JOIN driver d  ON res.fk_driver_id = d._id
        JOIN race r    ON res.fk_race_id = r._id
        WHERE r.fk_circuit_id = :circuit_id
            AND res.grid IS NOT NULL
            AND res.position IS NOT NULL
        ORDER BY diff DESC
        LIMIT 1;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'circuit_id': circuit_id})