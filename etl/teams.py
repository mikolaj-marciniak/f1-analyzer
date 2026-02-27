import pandas as pd
from fastf1.ergast import Ergast

from sqlalchemy.engine import Engine
from sqlalchemy import text

ergast = Ergast()

def extract_teams() -> pd.DataFrame:
    limit = 30
    offset = 0
    chunks = []

    while True:
        resp = ergast.get_constructor_info(limit=limit, offset=offset)

        if resp is None or resp.empty:
            break

        chunks.append(resp)
        offset += limit

        if len(resp) < limit:
            break

    return (pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()).copy()

def transform_teams(teams_df: pd.DataFrame) -> pd.DataFrame:
    required = {'constructorId', 'constructorName', 'constructorNationality'}
    missing = required - set(teams_df.columns)
    if missing:
        raise ValueError(f"Missing columns in transform_teams: {missing}")
    
    df = teams_df.copy()

    df.rename(columns={'constructorId': 'source_team_id', 'constructorName': 'name', 'constructorNationality': 'nationality'}, inplace=True)
    df.dropna(subset=['source_team_id', 'name'], inplace=True)
    df.drop_duplicates(subset=['source_team_id'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df[['source_team_id', 'name', 'nationality']]

def load_teams(engine: Engine, teams_df: pd.DataFrame) -> None:
    required = {'source_team_id', 'name', 'nationality'}
    missing = required - set(teams_df.columns)
    if missing:
        raise ValueError(f"Missing columns in load_teams: {missing}")
    
    stmt = text("""
        INSERT INTO team(source_team_id, name, nationality)
        VALUES (:source_team_id, :name, :nationality)
        ON CONFLICT (source_team_id) DO UPDATE
        SET name = EXCLUDED.name,
            nationality = EXCLUDED.nationality
        WHERE team.name IS DISTINCT FROM EXCLUDED.name
            OR team.nationality IS DISTINCT FROM EXCLUDED.nationality;
    """)

    records = teams_df[['source_team_id', 'name', 'nationality']].to_dict(orient="records")

    with engine.begin() as conn:
        conn.execute(stmt, records)