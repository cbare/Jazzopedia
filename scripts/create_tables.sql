CREATE TABLE IF NOT EXISTS Session(
  id                INTEGER PRIMARY KEY ASC,
  jd_sort_key       INTEGER,
  place             TEXT,
  `date`            TEXT,
  notes             TEXT
);

CREATE TABLE IF NOT EXISTS Part(
  id                INTEGER PRIMARY KEY ASC,
  session_id        INTEGER,
  personnel         TEXT
);

CREATE TABLE IF NOT EXISTS Track(
  id                INTEGER PRIMARY KEY ASC,
  part_id           INTEGER,
  name              INTEGER,
  issued            TEXT,
  catalog_id        TEXT,
  length            TEXT                        -- track length in MM:SS
);

CREATE TABLE IF NOT EXISTS Person(
  id                INTEGER PRIMARY KEY ASC,
  name              TEXT,
  full_name         TEXT,
  slug              TEXT,
  birth_date        TEXT,
  birth_place       TEXT,
  death_date        TEXT,
  death_place       TEXT
);

CREATE TABLE IF NOT EXISTS `Group`(
  id                INTEGER PRIMARY KEY ASC,
  name              TEXT,
  description       TEXT,
  slug              TEXT
);

CREATE TABLE IF NOT EXISTS Person_Part(
  person_id         INTEGER,
  part_id           INTEGER,
  role              TEXT                                          
);

CREATE TABLE IF NOT EXISTS Data_Source(
  entity_id         INTEGER,
  entity_type       TEXT,
  source            TEXT,
  url               TEXT,
  data_quality      TEXT                        -- verified, unverified, error??
);

