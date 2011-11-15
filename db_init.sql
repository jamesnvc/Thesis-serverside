CREATE TABLE tracks (
  id SERIAL PRIMARY KEY,
  release INT,
  intensity REAL,
  song TEXT
);

CREATE TABLE targets (
  id SERIAL PRIMARY KEY,
  name TEXT
);

CREATE TABLE track_target (
  track_id INT,
  target_id INT
);
