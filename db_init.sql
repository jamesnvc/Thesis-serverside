-- Track has many blocks
CREATE TABLE tracks (
  id SERIAL PRIMARY KEY,
  has_pdf BOOLEAN,
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
-- TODO: Rename to sequence, break this into moves
CREATE TABLE exercises (
  id SERIAL PRIMARY KEY,
  block_id INT,
  description TEXT,
  reps INT,
  gear INT,
  start_time INT,
  length INT
);

CREATE TABLE moves (
  id SERIAL PRIMARY KEY,
  sequence INT,
  exercise_id INT,
  description TEXT,
  count INT
);

-- Target has and belongs to many moves
CREATE TABLE targets (
  id SERIAL PRIMARY KEY,
  name TEXT
);

CREATE TABLE move_target (
  move_id INT,
  target_id INT
);
