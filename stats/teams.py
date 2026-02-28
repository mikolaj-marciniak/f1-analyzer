import pandas as pd
from sqlalchemy import text
from db.engine import get_engine

def get_teams(ascending: bool = True) -> pd.DataFrame:
    order = "ASC" if ascending else "DESC"

    sql = text(f"""
        SELECT _id, name
        FROM team
        ORDER BY name {order};
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn)
    
def get_teams_by_season(season: int, ascending: bool = True) -> pd.DataFrame:
    order = "ASC" if ascending else "DESC"

    sql = text(f"""
        SELECT team._id, team.name
        FROM result
        JOIN race ON result.fk_race_id = race._id
        JOIN team ON result.fk_team_id = team._id
        WHERE race.season = :season
        GROUP BY team._id, team.name
        ORDER BY team.name {order};
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'season': season})
    
def get_team_data(team_id: int) -> pd.DataFrame:
    sql = text("""
        SELECT _id, name, nationality
        FROM team
        WHERE _id = :team_id;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'team_id': team_id})

def get_best_circuit_of_team(team_id: int) -> pd.DataFrame:
    sql = text("""
        SELECT c.name, c.location, c.country, AVG(res.position::numeric) as mean_pos
        FROM result res
        JOIN race r    ON res.fk_race_id = r._id
        JOIN circuit c ON r.fk_circuit_id = c._id
        WHERE res.fk_team_id = :team_id
            AND res.position IS NOT NULL
        GROUP BY c._id, c.name, c.location, c.country
        ORDER BY mean_pos ASC
        LIMIT 1;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'team_id': team_id})

def get_most_gained_positions_by_team(team_id: int) -> pd.DataFrame:
    sql = text("""
        SELECT (res.grid - res.position) diff
        FROM result res
        WHERE res.fk_team_id = :team_id
            AND res.grid IS NOT NULL
            AND res.position IS NOT NULL
        ORDER BY diff DESC
        LIMIT 1;
    """)

    engine = get_engine()
    with engine.begin() as conn:
        return pd.read_sql(sql, conn, params={'team_id': team_id})