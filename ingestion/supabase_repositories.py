"""
supabase_repositories.py

Mirrors the interface of repositories.py but targets Supabase (Postgres)
via psycopg2. Uses %s placeholders instead of SQLite's ?.

All functions accept an open psycopg2 connection; committing is the
caller's responsibility (handled by cloud_publisher._worker).
"""

from constants import SESSION_STATUS_ACTIVE, SESSION_STATUS_ENDED


def upsert_device(*, conn, device_id: str, seen_ts: str, status: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO devices (device_id, first_seen_at, last_seen_at, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (device_id) DO UPDATE SET
                last_seen_at = EXCLUDED.last_seen_at,
                status       = EXCLUDED.status
            """,
            (device_id, seen_ts, seen_ts, status),
        )


def create_session_if_missing(*, conn, session_id: str, device_id: str, started_at: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO sessions (
                session_id, device_id, started_at,
                ended_at, duration_ms, interaction_count, status
            )
            VALUES (%s, %s, %s, NULL, NULL, 0, %s)
            ON CONFLICT (session_id) DO NOTHING
            """,
            (session_id, device_id, started_at, SESSION_STATUS_ACTIVE),
        )


def insert_event(
    *,
    conn,
    device_id: str,
    session_id: str | None,
    event_type: str,
    event_ts: str,
    received_ts: str,
    topic: str,
    payload_json: str,
) -> None:
    # Supabase uses BIGSERIAL for events.id — we let Postgres assign it.
    # payload_json is stored as JSONB; psycopg2 passes the string and Postgres casts it.
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO events (
                device_id, session_id, event_type,
                event_ts, received_ts, topic, payload_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
            """,
            (device_id, session_id, event_type, event_ts, received_ts, topic, payload_json),
        )


def insert_switch_event(
    *,
    conn,
    session_id: str,
    device_id: str,
    switch_name: str,
    value: int,
    event_ts: str,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO switch_events (session_id, device_id, switch_name, value, event_ts)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (session_id, device_id, switch_name, value, event_ts),
        )


def increment_session_interaction_count(*, conn, session_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE sessions
            SET interaction_count = interaction_count + 1
            WHERE session_id = %s AND status = %s
            """,
            (session_id, SESSION_STATUS_ACTIVE),
        )


def end_session(
    *,
    conn,
    session_id: str,
    ended_at: str,
    duration_ms: int,
    interaction_count: int,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE sessions
            SET
                ended_at          = %s,
                duration_ms       = %s,
                interaction_count = %s,
                status            = %s
            WHERE session_id = %s AND status = %s
            """,
            (ended_at, duration_ms, interaction_count, SESSION_STATUS_ENDED,
             session_id, SESSION_STATUS_ACTIVE),
        )
