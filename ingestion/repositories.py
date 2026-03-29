from constants import SESSION_STATUS_ACTIVE, SESSION_STATUS_ENDED


def upsert_device(*, conn, device_id: str, seen_ts: str, status: str) -> None:
    conn.execute(
        """
        INSERT INTO devices (device_id, first_seen_at, last_seen_at, status)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(device_id) DO UPDATE SET
          last_seen_at = excluded.last_seen_at,
          status = excluded.status
        """,
        (device_id, seen_ts, seen_ts, status),
    )


def create_session_if_missing(*, conn, session_id: str, device_id: str, started_at: str) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO sessions (
          session_id,
          device_id,
          started_at,
          ended_at,
          duration_ms,
          interaction_count,
          status
        )
        VALUES (?, ?, ?, NULL, NULL, 0, ?)
        """,
        (session_id, device_id, started_at, SESSION_STATUS_ACTIVE),
    )


def get_session_row(*, conn, session_id: str):
    cursor = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        (session_id,),
    )
    return cursor.fetchone()


def get_active_sessions_for_device(*, conn, device_id: str) -> list:
    cursor = conn.execute(
        "SELECT * FROM sessions WHERE device_id = ? AND status = ?",
        (device_id, SESSION_STATUS_ACTIVE),
    )
    return cursor.fetchall()


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
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO events (
          device_id,
          session_id,
          event_type,
          event_ts,
          received_ts,
          topic,
          payload_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (device_id, session_id, event_type, event_ts, received_ts, topic, payload_json),
    )
    return int(cursor.lastrowid)


def insert_switch_event(
    *,
    conn,
    session_id: str,
    device_id: str,
    switch_name: str,
    value: int,
    event_ts: str,
    event_id: int,
) -> None:
    conn.execute(
        """
        INSERT INTO switch_events (
          session_id,
          device_id,
          switch_name,
          value,
          event_ts,
          event_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (session_id, device_id, switch_name, value, event_ts, event_id),
    )


def increment_session_interaction_count(*, conn, session_id: str) -> None:
    conn.execute(
        """
        UPDATE sessions
        SET interaction_count = interaction_count + 1
        WHERE session_id = ? AND status = ?
        """,
        (session_id, SESSION_STATUS_ACTIVE),
    )


def end_session(
    *,
    conn,
    session_id: str,
    ended_at: str,
    duration_ms: int,
    interaction_count: int | None,
) -> bool:
    row = get_session_row(conn=conn, session_id=session_id)
    if row is None or row["status"] != SESSION_STATUS_ACTIVE:
        return False

    final_interaction_count = (
        interaction_count if interaction_count is not None else int(row["interaction_count"])
    )

    cursor = conn.execute(
        """
        UPDATE sessions
        SET
          ended_at = ?,
          duration_ms = ?,
          interaction_count = ?,
          status = ?
        WHERE session_id = ? AND status = ?
        """,
        (
            ended_at,
            duration_ms,
            final_interaction_count,
            SESSION_STATUS_ENDED,
            session_id,
            SESSION_STATUS_ACTIVE,
        ),
    )
    return cursor.rowcount > 0