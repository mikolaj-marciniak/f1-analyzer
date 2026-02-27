import pandas as pd
import fastf1
from .circuits import slugify_circuit
from sqlalchemy.engine import Engine
from sqlalchemy import text

def extract_races(season: int) -> pd.DataFrame:
    schedule = fastf1.get_event_schedule(season).copy()
    schedule['Season'] = season
    return schedule[schedule['RoundNumber'] != 0][['Season', 'RoundNumber', 'Location', 'Country']]

def transform_races(races_df: pd.DataFrame) -> pd.DataFrame:
    required = {'Season', 'RoundNumber', 'Location', 'Country'}
    missing = required - set(races_df.columns)
    if missing:
        raise ValueError(f"Missing columns in transform_races: {missing}")
    
    df = races_df.copy()

    df.rename(columns={'Season': 'season', 'RoundNumber': 'round', 'Location': 'name', 'Country': 'country'}, inplace=True)
    df['circuit_slug'] = df.apply(slugify_circuit, axis=1)

    df.dropna(subset=['season', 'round', 'circuit_slug'], inplace=True)
    df.drop_duplicates(subset=['season', 'round'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df[['season', 'round', 'circuit_slug']]

def load_races(engine: Engine, races_df: pd.DataFrame) -> None:
    required = {'season', 'round', 'circuit_slug'}
    missing = required - set(races_df.columns)
    if missing:
        raise ValueError(f"Missing columns in load_races: {missing}")
    
    df = races_df.copy()
    
    with engine.begin() as conn:
        circuits = conn.execute(text("SELECT _id, slug FROM circuit")).fetchall()
        circuit_map = {slug: _id for (_id, slug) in circuits}
        df['fk_circuit_id'] = df['circuit_slug'].map(circuit_map)

        missing_slugs = df.loc[df['fk_circuit_id'].isna(), 'circuit_slug'].unique().tolist()
        if missing_slugs:
            raise ValueError(f"Brakuje circuitów w DB dla slugów: {missing_slugs}")
        
        df['fk_circuit_id'] = df['fk_circuit_id'].astype(int)
    
        stmt = text("""
            INSERT INTO race(season, round, fk_circuit_id)
            VALUES (:season, :round, :fk_circuit_id)
            ON CONFLICT (season, round) DO UPDATE
            SET fk_circuit_id = EXCLUDED.fk_circuit_id
            WHERE race.fk_circuit_id != EXCLUDED.fk_circuit_id;
        """)

        records = df[['season', 'round', 'fk_circuit_id']].to_dict(orient="records")

        conn.execute(stmt, records)