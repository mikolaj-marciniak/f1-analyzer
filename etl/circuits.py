import pandas as pd
from fastf1.ergast import Ergast

from sqlalchemy.engine import Engine
from sqlalchemy import text

ergast = Ergast()

def extract_circuits() -> pd.DataFrame:
    limit = 30
    offset = 0
    chunks = []

    while True:
        resp = ergast.get_circuits(limit=limit, offset=offset)

        if resp is None or resp.empty:
            break

        chunks.append(resp)
        offset += limit

        if len(resp) < limit:
            break

    return (pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()).copy()

def transform_circuits(circuits_df: pd.DataFrame) -> pd.DataFrame:
    required = {'circuitId', 'circuitName', 'locality', 'country'}
    missing = required - set(circuits_df.columns)
    if missing:
        raise ValueError(f"Missing columns in transform_circuits: {missing}")
    
    df = circuits_df[['circuitId', 'circuitName', 'locality', 'country']].copy()
    
    df.rename(columns={'circuitId': 'source_circuit_id', 'circuitName': 'name', 'locality': 'location', 'country': 'country'}, inplace=True)

    df.dropna(subset=['source_circuit_id', 'name', 'location', 'country'], inplace=True)
    df.drop_duplicates(subset=['source_circuit_id'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df[['source_circuit_id', 'name', 'location', 'country']].copy()

def load_circuits(engine: Engine, circuits_df: pd.DataFrame) -> None:
    required = {'source_circuit_id', 'name', 'location', 'country'}
    missing = required - set(circuits_df.columns)
    if missing:
        raise ValueError(f"Missing columns in load_circuits: {missing}")
    
    stmt = text("""
        INSERT INTO circuit(source_circuit_id, name, location, country)
        VALUES (:source_circuit_id, :name, :location, :country)
        ON CONFLICT (source_circuit_id) DO UPDATE
        SET name = EXCLUDED.name,
            location = EXCLUDED.location,
            country = EXCLUDED.country
        WHERE circuit.name IS DISTINCT FROM EXCLUDED.name
            OR circuit.location IS DISTINCT FROM EXCLUDED.location
            OR circuit.country IS DISTINCT FROM EXCLUDED.country;
    """)

    records = circuits_df[['source_circuit_id', 'name', 'location', 'country']].to_dict(orient="records")

    with engine.begin() as conn:
        conn.execute(stmt, records)