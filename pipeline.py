from sqlalchemy.engine import Engine

from db.engine import get_engine
from db.init import init_db
from db.drop import drop_db

from etl.circuits import extract_circuits, transform_circuits, load_circuits
from etl.drivers import extract_drivers, transform_drivers, load_drivers
from etl.teams import extract_teams, transform_teams, load_teams
from etl.races import extract_races, transform_races, load_races
from etl.results import extract_results, transform_results, load_results

from fastf1.ergast import Ergast
from datetime import date

from get_last_season import get_last_loaded_season

ergast = Ergast()

def load_data(start: int, end: int, engine: Engine | None = None) -> None:
    if engine is None:
        engine = get_engine()

    load_circuits(engine, transform_circuits(extract_circuits()))
    load_drivers(engine, transform_drivers(extract_drivers()))
    load_teams(engine, transform_teams(extract_teams()))

    for season in range(start, end + 1):
        load_races(engine, transform_races(extract_races(season)))

    for season in range(start, end + 1):
        load_results(engine, transform_results(extract_results(season)))

def load_full_data(engine: Engine | None = None) -> None:
    if engine is None:
        engine = get_engine()

    start = 1950
    end = date.today().year
    load_data(start, end, engine)

def full_data_reload(engine: Engine | None = None) -> None:
    if engine is None:
        engine = get_engine()

    drop_db(engine)
    init_db(engine)
    load_full_data(engine)

def partial_reload(engine: Engine | None = None) -> None:
    if engine is None:
        engine = get_engine()

    start = get_last_loaded_season(engine)
    if start is None:
        full_data_reload(engine)
    else:
        end = date.today().year
        load_data(start, end, engine)