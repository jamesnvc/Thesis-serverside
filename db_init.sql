-- Track has many blocks
CREATE TABLE tracks (
  id SERIAL PRIMARY KEY,
  sequence INT,
  release INT,
  song TEXT,
  kind TEXT,
  length_minutes INT,
  length_seconds INT
);

-- Block belongs to a track, has many exercises
CREATE TABLE blocks (
  id SERIAL PRIMARY KEY,
  track_id INT,
  sequence INT,
  description TEXT
);

-- Exercise belongs to a block, has many targets
CREATE TABLE exercises (
  id SERIAL PRIMARY KEY,
  block_id INT,
  description TEXT,
  count INT,
  reps INT,
  gear INT,
  start_time INT
);

-- Target has and belongs to many exercises
CREATE TABLE targets (
  id SERIAL PRIMARY KEY,
  name TEXT
);

CREATE TABLE exercise_target (
  exercise_id INT,
  target_id INT
);
