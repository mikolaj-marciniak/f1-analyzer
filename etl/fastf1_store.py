import pandas as pd
import fastf1

data = {}

def load_data(season: int) -> None:
    global data

    schedule = fastf1.get_event_schedule(season)

    data_frames = []

    for _, event in schedule.iterrows():
        number = int(event['RoundNumber'])
        if number != 0:
            race = fastf1.get_session(season, number, "R")
            race.load()
            results = race.results
            if results is None or results.empty:
                continue
            results = results.copy()
            results['Season'] = season
            results['RoundNumber'] = number
            data_frames.append(results)
    data[season] = pd.concat(data_frames, ignore_index=True) if data_frames else pd.DataFrame()

def get_data(season: int) -> pd.DataFrame:
    if season not in data:
        load_data(season)

    return data[season].copy()