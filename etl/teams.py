import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text
from .fastf1_store import get_data

def extract_teams(season: int) -> pd.DataFrame:
    return get_data(season)[['TeamId', 'TeamName', 'TeamColor']]

def transform_teams(teams_df: pd.DataFrame) -> pd.DataFrame:
    required = {'TeamId', 'TeamName', 'TeamColor'}
    missing = required - set(teams_df.columns)
    if missing:
        raise ValueError(f"Missing columns in transform_teams: {missing}")
    
    df = teams_df.copy()

    df.rename(columns={'TeamId': 'source_team_id', 'TeamName': 'name', 'TeamColor': 'color'}, inplace=True)
    df.dropna(subset=['source_team_id', 'name'], inplace=True)
    df.drop_duplicates(subset=['source_team_id'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df[['source_team_id', 'name', 'color']]

def load_teams(engine: Engine, teams_df: pd.DataFrame) -> None:
    required = {'source_team_id', 'name', 'color'}
    missing = required - set(teams_df.columns)
    if missing:
        raise ValueError(f"Missing columns in load_teams: {missing}")
    
    stmt = text("""
        INSERT INTO team(source_team_id, name, color)
        VALUES (:source_team_id, :name, :color)
        ON CONFLICT (source_team_id) DO UPDATE
        SET name = EXCLUDED.name,
            color = EXCLUDED.color
        WHERE team.name != EXCLUDED.name
            OR team.color IS DISTINCT FROM EXCLUDED.color;
    """)

    records = teams_df[['source_team_id', 'name', 'color']].to_dict(orient="records")

    with engine.begin() as conn:
        conn.execute(stmt, records)