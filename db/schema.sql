--CIRCUITS
CREATE TABLE IF NOT EXISTS circuit (
    _id SERIAL PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    country TEXT NOT NULL
);

--DRIVERS
CREATE TABLE IF NOT EXISTS driver (
    _id SERIAL PRIMARY KEY,
    source_driver_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    abbreviation TEXT NOT NULL
);

--TEAMS
CREATE TABLE IF NOT EXISTS team (
    _id SERIAL PRIMARY KEY,
    source_team_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    color TEXT
);

--RACES
CREATE TABLE IF NOT EXISTS race (
    _id SERIAL PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    season INTEGER NOT NULL,
    round INTEGER NOT NULL,
    fk_circuit_id INTEGER NOT NULL,

    CONSTRAINT fk_circuit_id_constraint
        FOREIGN KEY (fk_circuit_id)
        REFERENCES circuit(_id)
        ON DELETE RESTRICT,
    
    CONSTRAINT uq_race_season_round UNIQUE (season, round)
);

--RESULTS
CREATE TABLE IF NOT EXISTS result (
    _id SERIAL PRIMARY KEY,
    fk_race_id INT NOT NULL,
    fk_driver_id INT NOT NULL,
    fk_team_id INT NOT NULL,
    position INT NOT NULL,
    points NUMERIC(5, 2) NOT NULL,

    CONSTRAINT fk_race_id_constraint
        FOREIGN KEY (fk_race_id)
        REFERENCES race(_id)
        ON DELETE RESTRICT,
    
    CONSTRAINT fk_driver_id_constraint
        FOREIGN KEY (fk_driver_id)
        REFERENCES driver(_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_team_id_constraint
        FOREIGN KEY (fk_team_id)
        REFERENCES team(_id)
        ON DELETE RESTRICT,

    CONSTRAINT uq_result_race_driver UNIQUE (fk_race_id, fk_driver_id)
);