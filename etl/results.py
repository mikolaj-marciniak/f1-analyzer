import pandas as pd
from .fastf1_store import get_data
from sqlalchemy.engine import Engine
from sqlalchemy import text

def extract_results(season: int) -> pd.DataFrame:
    return get_data(season)[['Season', 'RoundNumber', 'DriverId', 'TeamId', 'Position', 'Points']]

def transform_results(results_df: pd.DataFrame) -> pd.DataFrame:
    required = {'Season', 'RoundNumber', 'DriverId', 'TeamId', 'Position', 'Points'}
    missing = required - set(results_df.columns)
    if missing:
        raise ValueError(f"Missing columns in transform_results: {missing}")
    
    df = results_df.copy()

    df.rename(columns={'Season': 'season', 'RoundNumber': 'round', 'DriverId': 'source_driver_id', 'TeamId': 'source_team_id', 'Position': 'position', 'Points': 'points'}, inplace=True)
    df['race_key'] = list(zip(df['season'], df['round']))
    df.dropna(subset=['season', 'round', 'source_driver_id', 'source_team_id', 'position', 'points'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df[['season', 'round', 'source_driver_id', 'source_team_id', 'position', 'points', 'race_key']]

def load_results(engine: Engine, results_df: pd.DataFrame) -> None:
    required = {'season', 'round', 'source_driver_id', 'source_team_id', 'position', 'points', 'race_key'}
    missing = required - set(results_df.columns)
    if missing:
        raise ValueError(f"Missing columns in load_results: {missing}")
    
    df = results_df.copy()
    
    with engine.begin() as conn:
        races = conn.execute(text("SELECT _id, season, round FROM race")).fetchall()
        drivers = conn.execute(text("SELECT _id, source_driver_id FROM driver")).fetchall()
        teams = conn.execute(text("SELECT _id, source_team_id FROM team")).fetchall()

        race_map = {(season, round): _id for (_id, season, round) in races}
        driver_map = {source_driver_id: _id for (_id, source_driver_id) in drivers}
        team_map = {source_team_id: _id for (_id, source_team_id) in teams}

        df['fk_race_id'] = df['race_key'].map(race_map)
        df['fk_driver_id'] = df['source_driver_id'].map(driver_map)
        df['fk_team_id'] = df['source_team_id'].map(team_map)

        missing_races = df.loc[df['fk_race_id'].isna(), 'race_key'].unique().tolist()
        missing_drivers = df.loc[df['fk_driver_id'].isna(), 'source_driver_id'].unique().tolist()
        missing_teams = df.loc[df['fk_team_id'].isna(), 'source_team_id'].unique().tolist()

        if missing_races or missing_drivers or missing_teams:
            raise ValueError(f"Brakuje w DB: races={missing_races}, drivers={missing_drivers}, teams={missing_teams}")
        
        df['fk_race_id'] = df['fk_race_id'].astype(int)
        df['fk_driver_id'] = df['fk_driver_id'].astype(int)
        df['fk_team_id'] = df['fk_team_id'].astype(int)
        df["position"] = df["position"].astype(int)
        df["points"] = df["points"].astype(float).round(2)
    
        stmt = text("""
            INSERT INTO result(fk_race_id, fk_driver_id, fk_team_id, position, points)
            VALUES (:fk_race_id, :fk_driver_id, :fk_team_id, :position, :points)
            ON CONFLICT (fk_race_id, fk_driver_id) DO UPDATE
            SET fk_team_id = EXCLUDED.fk_team_id,
                position = EXCLUDED.position,
                points = EXCLUDED.points
            WHERE result.fk_team_id != EXCLUDED.fk_team_id
                OR result.position != EXCLUDED.position
                OR result.points != EXCLUDED.points;
        """)

        records = df[['fk_race_id', 'fk_driver_id', 'fk_team_id', 'position', 'points']].to_dict(orient="records")

        conn.execute(stmt, records)