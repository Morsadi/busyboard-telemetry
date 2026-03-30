from repositories import (
    create_session_if_missing,
    end_session,
    get_active_sessions_for_device,
    get_session_row,
    increment_session_interaction_count,
    insert_event,
    insert_switch_event,
    upsert_device,
)


def test_upsert_device_inserts_new_device(conn):
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:00:00+00:00",
        status="online",
    )
    conn.commit()

    row = conn.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        ("bb-123",),
    ).fetchone()

    assert row is not None
    assert row["device_id"] == "bb-123"
    assert row["status"] == "online"
    assert row["first_seen_at"] == "2026-03-26T16:00:00+00:00"
    assert row["last_seen_at"] == "2026-03-26T16:00:00+00:00"


def test_upsert_device_updates_existing_device(conn):
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:00:00+00:00",
        status="online",
    )
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:05:00+00:00",
        status="offline",
    )
    conn.commit()

    row = conn.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        ("bb-123",),
    ).fetchone()

    assert row["first_seen_at"] == "2026-03-26T16:00:00+00:00"
    assert row["last_seen_at"] == "2026-03-26T16:05:00+00:00"
    assert row["status"] == "offline"


def test_create_session_if_missing_inserts_once(conn):
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:00:00+00:00",
        status="online",
    )

    create_session_if_missing(
        conn=conn,
        session_id="sess-1",
        device_id="bb-123",
        started_at="2026-03-26T16:10:00+00:00",
    )
    create_session_if_missing(
        conn=conn,
        session_id="sess-1",
        device_id="bb-123",
        started_at="2026-03-26T16:10:00+00:00",
    )
    conn.commit()

    rows = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        ("sess-1",),
    ).fetchall()

    assert len(rows) == 1
    assert rows[0]["status"] == "active"
    assert rows[0]["interaction_count"] == 0


def test_get_session_row_returns_session(conn):
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:00:00+00:00",
        status="online",
    )
    create_session_if_missing(
        conn=conn,
        session_id="sess-1",
        device_id="bb-123",
        started_at="2026-03-26T16:10:00+00:00",
    )
    conn.commit()

    row = get_session_row(conn=conn, session_id="sess-1")

    assert row is not None
    assert row["session_id"] == "sess-1"
    assert row["device_id"] == "bb-123"


def test_get_active_sessions_for_device_returns_only_active(conn):
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:00:00+00:00",
        status="online",
    )

    create_session_if_missing(
        conn=conn,
        session_id="sess-active",
        device_id="bb-123",
        started_at="2026-03-26T16:10:00+00:00",
    )
    create_session_if_missing(
        conn=conn,
        session_id="sess-ended",
        device_id="bb-123",
        started_at="2026-03-26T16:11:00+00:00",
    )

    end_session(
        conn=conn,
        session_id="sess-ended",
        ended_at="2026-03-26T16:12:00+00:00",
        duration_ms=1000,
        interaction_count=0,
    )
    conn.commit()

    rows = get_active_sessions_for_device(conn=conn, device_id="bb-123")
    session_ids = {row["session_id"] for row in rows}

    assert session_ids == {"sess-active"}


def test_insert_event_creates_event_row(conn):
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:00:00+00:00",
        status="online",
    )

    event_id = insert_event(
        conn=conn,
        device_id="bb-123",
        session_id=None,
        event_type="device_connected",
        event_ts="2026-03-26T16:00:00+00:00",
        received_ts="2026-03-26T16:00:01+00:00",
        topic="busyboard/bb-123/events",
        payload_json='{"event":"device_connected"}',
    )
    conn.commit()

    row = conn.execute(
        "SELECT * FROM events WHERE id = ?",
        (event_id,),
    ).fetchone()

    assert row is not None
    assert row["device_id"] == "bb-123"
    assert row["event_type"] == "device_connected"


def test_insert_switch_event_creates_row(conn):
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:00:00+00:00",
        status="online",
    )
    create_session_if_missing(
        conn=conn,
        session_id="sess-1",
        device_id="bb-123",
        started_at="2026-03-26T16:10:00+00:00",
    )

    event_id = insert_event(
        conn=conn,
        device_id="bb-123",
        session_id="sess-1",
        event_type="switch_changed",
        event_ts="2026-03-26T16:10:01+00:00",
        received_ts="2026-03-26T16:10:01+00:00",
        topic="busyboard/bb-123/switch/SW1",
        payload_json='{"event":"switch_changed"}',
    )

    insert_switch_event(
        conn=conn,
        session_id="sess-1",
        device_id="bb-123",
        switch_name="SW1",
        value=1,
        event_ts="2026-03-26T16:10:01+00:00",
        event_id=event_id,
    )
    conn.commit()

    row = conn.execute(
        "SELECT * FROM switch_events WHERE event_id = ?",
        (event_id,),
    ).fetchone()

    assert row is not None
    assert row["session_id"] == "sess-1"
    assert row["switch_name"] == "SW1"
    assert row["value"] == 1


def test_increment_session_interaction_count_only_updates_active_session(conn):
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:00:00+00:00",
        status="online",
    )
    create_session_if_missing(
        conn=conn,
        session_id="sess-1",
        device_id="bb-123",
        started_at="2026-03-26T16:10:00+00:00",
    )

    increment_session_interaction_count(conn=conn, session_id="sess-1")
    increment_session_interaction_count(conn=conn, session_id="sess-1")
    conn.commit()

    row = get_session_row(conn=conn, session_id="sess-1")
    assert row["interaction_count"] == 2


def test_end_session_updates_active_session(conn):
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:00:00+00:00",
        status="online",
    )
    create_session_if_missing(
        conn=conn,
        session_id="sess-1",
        device_id="bb-123",
        started_at="2026-03-26T16:10:00+00:00",
    )

    did_end = end_session(
        conn=conn,
        session_id="sess-1",
        ended_at="2026-03-26T16:11:00+00:00",
        duration_ms=60000,
        interaction_count=3,
    )
    conn.commit()

    row = get_session_row(conn=conn, session_id="sess-1")

    assert did_end is True
    assert row["status"] == "ended"
    assert row["ended_at"] == "2026-03-26T16:11:00+00:00"
    assert row["duration_ms"] == 60000
    assert row["interaction_count"] == 3


def test_end_session_returns_false_for_missing_session(conn):
    did_end = end_session(
        conn=conn,
        session_id="missing",
        ended_at="2026-03-26T16:11:00+00:00",
        duration_ms=60000,
        interaction_count=1,
    )

    assert did_end is False


def test_end_session_returns_false_for_already_ended_session(conn):
    upsert_device(
        conn=conn,
        device_id="bb-123",
        seen_ts="2026-03-26T16:00:00+00:00",
        status="online",
    )
    create_session_if_missing(
        conn=conn,
        session_id="sess-1",
        device_id="bb-123",
        started_at="2026-03-26T16:10:00+00:00",
    )

    first_end = end_session(
        conn=conn,
        session_id="sess-1",
        ended_at="2026-03-26T16:11:00+00:00",
        duration_ms=60000,
        interaction_count=1,
    )
    second_end = end_session(
        conn=conn,
        session_id="sess-1",
        ended_at="2026-03-26T16:12:00+00:00",
        duration_ms=70000,
        interaction_count=2,
    )
    conn.commit()

    row = get_session_row(conn=conn, session_id="sess-1")

    assert first_end is True
    assert second_end is False
    assert row["ended_at"] == "2026-03-26T16:11:00+00:00"
    assert row["interaction_count"] == 1