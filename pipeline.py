from sqlalchemy.engine import Engine

from db.engine import get_engine
from db.init import init_db

# from etl.fastf1_store import load_data
# from etl.circuits import extract_circuits, transform_circuits, load_circuits
# from etl.drivers import extract_drivers, transform_drivers, load_drivers
# from etl.teams import extract_teams, transform_teams, load_teams
# from etl.races import extract_races, transform_races, load_races
# from etl.results import extract_results, transform_results, load_results

from fastf1.ergast import Ergast

def run(season: int, engine: Engine | None = None) -> None:
    if engine is None:
        engine = get_engine()

    init_db(engine)

    # load_data(season)

    # load_circuits(engine, transform_circuits(extract_circuits(season)))
    # load_drivers(engine, transform_drivers(extract_drivers(season)))
    # load_teams(engine, transform_teams(extract_teams(season)))
    # load_races(engine, transform_races(extract_races(season)))
    # load_results(engine, transform_results(extract_results(season)))
    ergast = Ergast()
    print(ergast.get_race_results(season=2024, round=1).content[0]['driverId'])
    print(ergast.get_driver_info().tail())
    print(ergast.get_race_results(2024).content[0])
    print(ergast.get_race_results(2024).content[0].columns)
    print(ergast.get_race_results(season, 5).content[0])


if __name__ == "__main__":
    run(2024)