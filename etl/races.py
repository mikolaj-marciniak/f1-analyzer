import pandas as pd
from fastf1.ergast import Ergast

from sqlalchemy.engine import Engine
from sqlalchemy import text

ergast = Ergast()

def extract_races(season: int) -> pd.DataFrame:
    return ergast.get_race_schedule(season=season).copy()

def transform_races(races_df: pd.DataFrame) -> pd.DataFrame:
    required = {'season', 'round', 'circuitId'}
    missing = required - set(races_df.columns)
    if missing:
        raise ValueError(f"Missing columns in transform_races: {missing}")
    
    df = races_df.copy()

    df.dropna(subset=['season', 'round', 'circuitId'], inplace=True)
    df.drop_duplicates(subset=['season', 'round'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df[['season', 'round', 'circuitId']]

def load_races(engine: Engine, races_df: pd.DataFrame) -> None:
    required = {'season', 'round', 'circuitId'}
    missing = required - set(races_df.columns)
    if missing:
        raise ValueError(f"Missing columns in load_races: {missing}")
    
    df = races_df.copy()
    
    with engine.begin() as conn:
        circuits = conn.execute(text("SELECT _id, source_circuit_id FROM circuit")).fetchall()
        circuit_map = {source_circuit_id: _id for (_id, source_circuit_id) in circuits}
        df['fk_circuit_id'] = df['circuitId'].map(circuit_map)

        missing = df.loc[df['fk_circuit_id'].isna(), 'circuitId'].unique().tolist()
        if missing:
            raise ValueError(f"Brakuje circuitów w DB dla circuitId: {missing}")
        
        df['fk_circuit_id'] = df['fk_circuit_id'].astype(int)
    
        stmt = text("""
            INSERT INTO race(season, round, fk_circuit_id)
            VALUES (:season, :round, :fk_circuit_id)
            ON CONFLICT (season, round) DO UPDATE
            SET fk_circuit_id = EXCLUDED.fk_circuit_id
            WHERE race.fk_circuit_id IS DISTINCT FROM EXCLUDED.fk_circuit_id;
        """)

        records = df[['season', 'round', 'fk_circuit_id']].to_dict(orient="records")

        conn.execute(stmt, records)