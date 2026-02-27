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
    season INTEGER NOT NULL CHECK (season >= 1950),
    round INTEGER NOT NULL CHECK (round >= 1),
    fk_circuit_id INTEGER NOT NULL,

    CONSTRAINT fk_circuit_id_constraint
        FOREIGN KEY (fk_circuit_id)
        REFERENCES circuit(_id)
        ON DELETE RESTRICT,
    
    CONSTRAINT uq_race_season_round UNIQUE (season, round)
);

--RACES-INDEXES
CREATE INDEX IF NOT EXISTS idx_race_fk_circuit_id ON race(fk_circuit_id);

--RESULTS
CREATE TABLE IF NOT EXISTS result (
    _id SERIAL PRIMARY KEY,
    fk_race_id INTEGER NOT NULL,
    fk_driver_id INTEGER NOT NULL,
    fk_team_id INTEGER NOT NULL,
    position INTEGER NOT NULL CHECK (position >= 1),
    points NUMERIC(5, 2) NOT NULL CHECK (points >= 0),

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

--RESULTS-INDEXES
CREATE INDEX IF NOT EXISTS idx_result_fk_race_id ON result(fk_race_id);
CREATE INDEX IF NOT EXISTS idx_result_fk_driver_id ON result(fk_driver_id);
CREATE INDEX IF NOT EXISTS idx_result_fk_team_id ON result(fk_team_id);