PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS devices (
  device_id      TEXT PRIMARY KEY,
  first_seen_at  TEXT NOT NULL,
  last_seen_at   TEXT NOT NULL,
  status         TEXT NOT NULL CHECK (status IN ('online', 'offline'))
);

CREATE TABLE IF NOT EXISTS sessions (
  session_id         TEXT PRIMARY KEY,
  device_id          TEXT NOT NULL,
  started_at         TEXT NOT NULL,
  ended_at           TEXT,
  duration_ms        INTEGER,
  interaction_count  INTEGER NOT NULL DEFAULT 0 CHECK (interaction_count >= 0),
  status             TEXT NOT NULL CHECK (status IN ('active', 'ended')),
  FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

CREATE TABLE IF NOT EXISTS events (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  device_id     TEXT NOT NULL,
  session_id    TEXT,
  event_type    TEXT NOT NULL,
  event_ts      TEXT NOT NULL,
  received_ts   TEXT NOT NULL,
  topic         TEXT NOT NULL,
  payload_json  TEXT NOT NULL,
  FOREIGN KEY (device_id) REFERENCES devices(device_id),
  FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS switch_events (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id   TEXT NOT NULL,
  device_id    TEXT NOT NULL,
  switch_name  TEXT NOT NULL,
  value        INTEGER NOT NULL CHECK (value IN (0, 1)),
  event_ts     TEXT NOT NULL,
  event_id     INTEGER UNIQUE,
  FOREIGN KEY (session_id) REFERENCES sessions(session_id),
  FOREIGN KEY (device_id) REFERENCES devices(device_id),
  FOREIGN KEY (event_id) REFERENCES events(id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_device_id           ON sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status              ON sessions(status);

CREATE INDEX IF NOT EXISTS idx_events_device_id             ON events(device_id);
CREATE INDEX IF NOT EXISTS idx_events_session_id            ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type            ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_event_ts              ON events(event_ts);

CREATE INDEX IF NOT EXISTS idx_switch_events_session_id     ON switch_events(session_id);
CREATE INDEX IF NOT EXISTS idx_switch_events_device_id      ON switch_events(device_id);
CREATE INDEX IF NOT EXISTS idx_switch_events_switch_name    ON switch_events(switch_name);
CREATE INDEX IF NOT EXISTS idx_switch_events_event_ts       ON switch_events(event_ts);