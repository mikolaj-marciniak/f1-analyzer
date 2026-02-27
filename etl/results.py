import pandas as pd
from fastf1.ergast import Ergast

from sqlalchemy.engine import Engine
from sqlalchemy import text

ergast = Ergast()

def extract_results(season: int) -> pd.DataFrame:
    number_of_rounds = ergast.get_race_schedule(season)['season'].count()
    chunks = []

    for i in range(number_of_rounds):
        df = ergast.get_race_results(season, i+1).content[0]
        df['season'] = season
        df['round'] = i+1
        chunks.append(df)

    return pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()

def transform_results(results_df: pd.DataFrame) -> pd.DataFrame:
    required = {'season', 'round', 'position', 'points', 'grid', 'driverId', 'constructorId', 'fastestLapRank'}
    missing = required - set(results_df.columns)
    if missing:
        raise ValueError(f"Missing columns in transform_results: {missing}")
    
    df = results_df.copy()

    df.rename(columns={'season': 'season', 'round': 'round', 'driverId': 'source_driver_id', 'constructorId': 'source_team_id', 'position': 'position', 'points': 'points', 'grid': 'grid', 'fastestLapRank': 'fastest_lap_rank'}, inplace=True)
    df['race_key'] = list(zip(df['season'], df['round']))
    df.dropna(subset=['season', 'round', 'source_driver_id', 'source_team_id', 'position', 'points'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df[['season', 'round', 'source_driver_id', 'source_team_id', 'position', 'points', 'grid', 'fastest_lap_rank', 'race_key']]

def load_results(engine: Engine, results_df: pd.DataFrame) -> None:
    required = {'season', 'round', 'source_driver_id', 'source_team_id', 'position', 'points', 'grid', 'fastest_lap_rank'}
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
    
        stmt = text("""
            INSERT INTO result(fk_race_id, fk_driver_id, fk_team_id, position, points, grid, fastest_lap_rank)
            VALUES (:fk_race_id, :fk_driver_id, :fk_team_id, :position, :points, :grid, :fastest_lap_rank)
            ON CONFLICT (fk_race_id, fk_driver_id) DO UPDATE
            SET fk_team_id = EXCLUDED.fk_team_id,
                position = EXCLUDED.position,
                points = EXCLUDED.points,
                grid = EXCLUDED.grid,
                fastest_lap_rank = EXCLUDED.fastest_lap_rank    
            WHERE result.fk_team_id IS DISTINCT FROM EXCLUDED.fk_team_id
                OR result.position IS DISTINCT FROM EXCLUDED.position
                OR result.points IS DISTINCT FROM EXCLUDED.points
                OR result.grid IS DISTINCT FROM EXCLUDED.grid
                OR result.fastest_lap_rank IS DISTINCT FROM EXCLUDED.fastest_lap_rank;
        """)

        records = df[['fk_race_id', 'fk_driver_id', 'fk_team_id', 'position', 'points', 'grid', 'fastest_lap_rank']].to_dict(orient="records")

        conn.execute(stmt, records)