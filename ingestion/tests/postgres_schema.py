"""Minimal isolated test schema for current Postgres repository operations.

Not a deployment migration. Shared semantics: docs/data-model.md.
"""

POSTGRES_SCHEMA = """
CREATE TABLE devices (
    device_id TEXT PRIMARY KEY,
    first_seen_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES devices(device_id),
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    duration_ms BIGINT,
    interaction_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL
);
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES devices(device_id),
    session_id TEXT REFERENCES sessions(session_id),
    event_type TEXT NOT NULL,
    event_ts TIMESTAMPTZ NOT NULL,
    received_ts TIMESTAMPTZ NOT NULL,
    topic TEXT NOT NULL,
    payload_json JSONB NOT NULL
);
CREATE TABLE switch_events (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    device_id TEXT NOT NULL REFERENCES devices(device_id),
    switch_name TEXT NOT NULL,
    value SMALLINT NOT NULL,
    event_ts TIMESTAMPTZ NOT NULL
);
"""
