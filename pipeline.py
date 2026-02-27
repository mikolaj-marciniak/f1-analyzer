from sqlalchemy.engine import Engine

from db.engine import get_engine
from db.init import init_db

from etl.circuits import extract_circuits, transform_circuits, load_circuits
from etl.drivers import extract_drivers, transform_drivers, load_drivers
from etl.teams import extract_teams, transform_teams, load_teams
from etl.races import extract_races, transform_races, load_races
from etl.results import extract_results, transform_results, load_results

from fastf1.ergast import Ergast

ergast = Ergast()

def load_data():
    engine = get_engine()
    init_db(engine)
    run(1, engine)

def run(season: int, engine: Engine | None = None) -> None:
    load_circuits(engine, transform_circuits(extract_circuits()))
    load_drivers(engine, transform_drivers(extract_drivers()))
    load_teams(engine, transform_teams(extract_teams()))
    
    for season in range(2024, 2026):
        load_races(engine, transform_races(extract_races(season)))
        load_results(engine, transform_results(extract_results(season)))


if __name__ == "__main__":
    load_data()