import pandas as pd
from fastf1.ergast import Ergast

from sqlalchemy.engine import Engine
from sqlalchemy import text

ergast = Ergast()

import time
import random
import pandas as pd

def extract_races(season: int) -> pd.DataFrame:
    def should_retry(e: Exception) -> bool:
        msg = str(e).lower()
        return (
            "too many requests" in msg
            or "429" in msg
            or "rate limit" in msg
            or "timeout" in msg
            or "connection" in msg
            or "temporar" in msg
            or "service unavailable" in msg
        )

    max_tries = 10
    last_exc: Exception | None = None

    for attempt in range(1, max_tries + 1):
        try:
            # stały throttle + jitter
            time.sleep(1.4 + random.random() * 0.6)

            df = ergast.get_race_schedule(season=season)
            # FastF1 czasem zwraca None/empty w edge-case’ach
            return (df.copy() if df is not None else pd.DataFrame())

        except Exception as e:
            last_exc = e
            if not should_retry(e):
                raise

            backoff = min(90, 2 ** attempt) + random.random()
            time.sleep(backoff)

    raise RuntimeError(
        f"Nie udało się pobrać race_schedule dla sezonu {season} "
        f"po {max_tries} próbach. Ostatni błąd: {last_exc}"
    )

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