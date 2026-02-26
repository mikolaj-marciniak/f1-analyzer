import pandas as pd
import fastf1

data = {}

def load_data(season: int) -> None:
    global data

    schedule = fastf1.get_event_schedule(season)

    all_results = pd.DataFrame()

    for _, event in schedule.iterrows():
        number = int(event['RoundNumber'])
        if number != 0:
            race = fastf1.get_session(season, number, "R")
            race.load()
            results = race.results
            all_results = pd.concat([all_results, results])
    data[season] = all_results

def get_data(season: int) -> pd.DataFrame:
    global data

    if season not in data:
        load_data(season)

    return data[season].copy()