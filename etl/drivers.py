import pandas as pd
from fastf1.ergast import Ergast

from sqlalchemy.engine import Engine
from sqlalchemy import text

ergast = Ergast()

def extract_drivers() -> pd.DataFrame:
    limit = 30
    offset = 0
    chunks = []

    while True:
        resp = ergast.get_driver_info(limit=limit, offset=offset)

        if resp is None or resp.empty:
            break

        chunks.append(resp)
        offset += limit

        if len(resp) < limit:
            break

    return (pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()).copy()

def transform_drivers(drivers_df: pd.DataFrame) -> pd.DataFrame:
    required = {'driverId', 'givenName', 'familyName', 'dateOfBirth', 'driverNationality'}
    missing = required - set(drivers_df.columns)
    if missing:
        raise ValueError(f"Missing columns in transform_drivers: {missing}")
    
    df = drivers_df.copy()

    df.rename(columns={'driverId': 'source_driver_id', 'givenName': 'name', 'familyName': 'family_name', 'dateOfBirth': 'date_of_birth', 'driverNationality': 'nationality'}, inplace=True)
    df.dropna(subset=['source_driver_id', 'name', 'family_name'], inplace=True)
    df.drop_duplicates(subset=['source_driver_id'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce').dt.date
    df['date_of_birth'] = df['date_of_birth'].where(df['date_of_birth'].notna(), None)

    return df[['source_driver_id', 'name', 'family_name', 'date_of_birth', 'nationality']]

def load_drivers(engine: Engine, drivers_df: pd.DataFrame) -> None:
    required = {'source_driver_id', 'name', 'family_name', 'date_of_birth', 'nationality'}
    missing = required - set(drivers_df.columns)
    if missing:
        raise ValueError(f"Missing columns in load_drivers: {missing}")
    
    stmt = text("""
        INSERT INTO driver(source_driver_id, name, family_name, date_of_birth, nationality)
        VALUES (:source_driver_id, :name, :family_name, :date_of_birth, :nationality)
        ON CONFLICT (source_driver_id) DO UPDATE
        SET name = EXCLUDED.name,
            family_name = EXCLUDED.family_name,
            date_of_birth = EXCLUDED.date_of_birth,
            nationality = EXCLUDED.nationality
        WHERE driver.name IS DISTINCT FROM EXCLUDED.name
            OR driver.family_name IS DISTINCT FROM EXCLUDED.family_name
            OR driver.date_of_birth IS DISTINCT FROM EXCLUDED.date_of_birth
            OR driver.nationality IS DISTINCT FROM EXCLUDED.nationality;
    """)

    records = drivers_df[['source_driver_id', 'name', 'family_name', 'date_of_birth', 'nationality']].to_dict(orient="records")

    with engine.begin() as conn:
        conn.execute(stmt, records)