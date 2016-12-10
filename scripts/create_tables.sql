CREATE TABLE IF NOT EXISTS Session(
  id                INTEGER PRIMARY KEY ASC,
  jd_sort_key       INTEGER,
  `group`           TEXT,
  place             TEXT,
  `date`            TEXT,
  notes             TEXT
);

CREATE TABLE IF NOT EXISTS Part(
  id                INTEGER PRIMARY KEY ASC,
  sort_order        INTEGER,
  session_id        INTEGER,
  personnel         TEXT,
  FOREIGN KEY(session_id) REFERENCES Session(id)
);
CREATE INDEX index_part ON Part(session_id);


CREATE TABLE IF NOT EXISTS Track(
  id                INTEGER PRIMARY KEY ASC,
  sort_order        INTEGER,
  part_id           INTEGER,
  name              INTEGER,
  issued            TEXT,
  catalog_id        TEXT,
  length            TEXT,                       -- track length in MM:SS
  FOREIGN KEY(part_id) REFERENCES Part(id)
);
CREATE INDEX index_track ON Track(part_id);

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
CREATE UNIQUE INDEX index_person_slug ON Person(slug COLLATE nocase);

CREATE TABLE IF NOT EXISTS `Group`(
  id                INTEGER PRIMARY KEY ASC,
  name              TEXT,
  description       TEXT,
  slug              TEXT
);
CREATE UNIQUE INDEX index_group_slug ON `Group`(slug COLLATE nocase);

CREATE TABLE IF NOT EXISTS Person_Part(
  person_id         INTEGER,
  part_id           INTEGER,
  role              TEXT,
  FOREIGN KEY(person_id) REFERENCES Person(id),
  FOREIGN KEY(part_id) REFERENCES Part(id)
);

CREATE TABLE IF NOT EXISTS Person_Session(
  person_id         INTEGER,
  session_id        INTEGER,
  FOREIGN KEY(person_id) REFERENCES Person(id),
  FOREIGN KEY(session_id) REFERENCES Session(id)
);

CREATE TABLE IF NOT EXISTS Data_Source(
  entity_id         INTEGER,
  entity_type       TEXT,
  source            TEXT,
  url               TEXT,
  data_quality      TEXT                        -- verified, unverified, error??, link??
);
CREATE INDEX index_data_source ON Data_Source(entity_id,entity_type);

