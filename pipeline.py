from sqlalchemy.engine import Engine

from db.engine import get_engine
from db.init_db import init_db

from etl.fastf1_store import load_data
from etl.circuits import extract_circuits, transform_circuits, load_circuits
from etl.drivers import extract_drivers, transform_drivers, load_drivers
from etl.teams import extract_teams, transform_teams, load_teams
from etl.races import extract_races, transform_races, load_races

import fastf1

def run(season: int, engine: Engine | None = None) -> None:
    if engine is None:
        engine = get_engine()

    init_db(engine)

    load_data(season)

    load_circuits(engine, transform_circuits(extract_circuits(season)))
    load_drivers(engine, transform_drivers(extract_drivers(season)))
    load_teams(engine, transform_teams(extract_teams(season)))
    load_races(engine, transform_races(extract_races(season)))

if __name__ == "__main__":
    run(2024)