import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text
import re
from .fastf1_store import get_data

def extract_drivers(season: int) -> pd.DataFrame:
    return get_data(season)[['DriverId', 'BroadcastName', 'Abbreviation']]

def transform_drivers(drivers_df: pd.DataFrame) -> pd.DataFrame:
    required = {'DriverId', 'BroadcastName', 'Abbreviation'}
    missing = required - set(drivers_df.columns)
    if missing:
        raise ValueError(f"Missing columns in transform_drivers: {missing}")
    
    df = drivers_df.copy()

    df.rename(columns={'DriverId': 'source_driver_id', 'BroadcastName': 'name', 'Abbreviation': 'abbreviation'}, inplace=True)
    df.dropna(subset=['source_driver_id', 'name', 'abbreviation'], inplace=True)
    df.drop_duplicates(subset=['source_driver_id'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['name'] = df['name'].apply(lambda name: re.sub(r"^\s*\d+\s+", "", name))

    return df[['source_driver_id', 'name', 'abbreviation']]

def load_drivers(engine: Engine, drivers_df: pd.DataFrame) -> None:
    required = {'source_driver_id', 'name', 'abbreviation'}
    missing = required - set(drivers_df.columns)
    if missing:
        raise ValueError(f"Missing columns in load_drivers: {missing}")
    
    stmt = text("""
        INSERT INTO driver(source_driver_id, name, abbreviation)
        VALUES (:source_driver_id, :name, :abbreviation)
        ON CONFLICT (source_driver_id) DO UPDATE
        SET name = EXCLUDED.name,
            abbreviation = EXCLUDED.abbreviation
        WHERE driver.name != EXCLUDED.name
            OR driver.abbreviation != EXCLUDED.abbreviation;
    """)

    records = drivers_df[['source_driver_id', 'name', 'abbreviation']].to_dict(orient="records")

    with engine.begin() as conn:
        conn.execute(stmt, records)