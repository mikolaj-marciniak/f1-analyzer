import fastf1
import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text
import re
import unicodedata

def extract_circuits(season: int) -> pd.DataFrame:
    schedule = fastf1.get_event_schedule(season)
    return schedule[['Location', 'Country']].copy()

def transform_circuits(circuits_df: pd.DataFrame) -> pd.DataFrame:
    required = {'Location', 'Country'}
    missing = required - set(circuits_df.columns)
    if missing:
        raise ValueError(f"Missing columns in transform_circuits: {missing}")
    
    df = circuits_df[['Location', 'Country']].copy()
    
    df.rename(columns={'Location': 'name', 'Country': 'country'}, inplace=True)
    df['slug'] = df.apply(slugify_circuit, axis=1)

    df.dropna(subset=['slug', 'name', 'country'], inplace=True)
    df.drop_duplicates(subset=['slug'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df[['slug', 'name', 'country']]

def load_circuits(engine: Engine, circuits_df: pd.DataFrame) -> None:
    required = {"slug", "name", "country"}
    missing = required - set(circuits_df.columns)
    if missing:
        raise ValueError(f"Missing columns in load_circuits: {missing}")
    
    stmt = text("""
        INSERT INTO circuit(slug, name, country)
        VALUES (:slug, :name, :country)
        ON CONFLICT (slug) DO UPDATE
        SET name = EXCLUDED.name,
            country = EXCLUDED.country
        WHERE circuit.name != EXCLUDED.name
            OR circuit.country != EXCLUDED.country;
    """)

    records = circuits_df[['slug', 'name', 'country']].to_dict(orient="records")

    with engine.begin() as conn:
        conn.execute(stmt, records)

def slugify_circuit(row: pd.Series) -> str:
    text = f"{row['name']}-{row['country']}".strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text