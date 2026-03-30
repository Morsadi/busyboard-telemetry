from handlers import (
    handle_device_connected,
    handle_device_offline,
    handle_device_online,
    handle_session_ended,
    handle_session_started,
    handle_switch_changed,
)


def test_handle_device_connected_marks_device_online_and_inserts_event(conn):
    handle_device_connected(
        topic="busyboard/bb-123/events",
        data={
            "event": "device_connected",
            "deviceId": "bb-123",
            "timestamp": "20260326164347",
        },
        received_ts="2026-03-26T16:43:47+00:00",
        payload_json='{"event":"device_connected","deviceId":"bb-123","timestamp":"20260326164347"}',
    )

    device = conn.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        ("bb-123",),
    ).fetchone()
    event = conn.execute(
        "SELECT * FROM events WHERE device_id = ? AND event_type = ?",
        ("bb-123", "device_connected"),
    ).fetchone()

    assert device is not None
    assert device["status"] == "online"
    assert event is not None


def test_handle_session_started_creates_session_and_event(conn):
    handle_session_started(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_started",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164347",
        },
        received_ts="2026-03-26T16:43:47+00:00",
        payload_json='{"event":"session_started","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164347"}',
    )

    session = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        ("sess-1",),
    ).fetchone()
    event = conn.execute(
        "SELECT * FROM events WHERE session_id = ? AND event_type = ?",
        ("sess-1", "session_started"),
    ).fetchone()

    assert session is not None
    assert session["status"] == "active"
    assert event is not None


def test_handle_switch_changed_creates_session_if_missing_and_increments_count(conn):
    handle_switch_changed(
        topic="busyboard/bb-123/switch/SW1",
        data={
            "event": "switch_changed",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "switch": "SW1",
            "value": 1,
            "timestamp": "20260326164348",
        },
        received_ts="2026-03-26T16:43:48+00:00",
        payload_json='{"event":"switch_changed","deviceId":"bb-123","sessionId":"sess-1","switch":"SW1","value":1,"timestamp":"20260326164348"}',
    )

    session = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        ("sess-1",),
    ).fetchone()
    switch_event = conn.execute(
        "SELECT * FROM switch_events WHERE session_id = ?",
        ("sess-1",),
    ).fetchone()

    assert session is not None
    assert session["status"] == "active"
    assert session["interaction_count"] == 1
    assert switch_event is not None
    assert switch_event["switch_name"] == "SW1"
    assert switch_event["value"] == 1


def test_handle_session_ended_ends_existing_session(conn):
    handle_session_started(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_started",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164347",
        },
        received_ts="2026-03-26T16:43:47+00:00",
        payload_json='{"event":"session_started","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164347"}',
    )

    handle_switch_changed(
        topic="busyboard/bb-123/switch/SW1",
        data={
            "event": "switch_changed",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "switch": "SW1",
            "value": 1,
            "timestamp": "20260326164348",
        },
        received_ts="2026-03-26T16:43:48+00:00",
        payload_json='{"event":"switch_changed","deviceId":"bb-123","sessionId":"sess-1","switch":"SW1","value":1,"timestamp":"20260326164348"}',
    )

    handle_session_ended(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_ended",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164350",
            "interactionCount": 1,
            "durationMs": 3000,
        },
        received_ts="2026-03-26T16:43:50+00:00",
        payload_json='{"event":"session_ended","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164350","interactionCount":1,"durationMs":3000}',
    )

    session = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        ("sess-1",),
    ).fetchone()
    event = conn.execute(
        "SELECT * FROM events WHERE session_id = ? AND event_type = ?",
        ("sess-1", "session_ended"),
    ).fetchone()

    assert session is not None
    assert session["status"] == "ended"
    assert session["interaction_count"] == 1
    assert session["duration_ms"] == 3000
    assert event is not None


def test_handle_device_offline_marks_device_offline_but_leaves_session_active(conn):
    handle_session_started(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_started",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164347",
        },
        received_ts="2026-03-26T16:43:47+00:00",
        payload_json='{"event":"session_started","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164347"}',
    )

    handle_device_offline(
        device_id="bb-123",
        received_ts="2026-03-26T16:44:00+00:00",
    )

    device = conn.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        ("bb-123",),
    ).fetchone()
    session = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        ("sess-1",),
    ).fetchone()

    assert device is not None
    assert device["status"] == "offline"
    assert session is not None
    assert session["status"] == "active"


def test_handle_device_online_marks_device_online(conn):
    handle_device_online(
        device_id="bb-123",
        received_ts="2026-03-26T16:44:00+00:00",
    )

    device = conn.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        ("bb-123",),
    ).fetchone()

    assert device is not None
    assert device["status"] == "online"


def test_handle_session_ended_ignores_unknown_session(conn):
    handle_session_ended(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_ended",
            "deviceId": "bb-123",
            "sessionId": "missing-session",
            "timestamp": "20260326164350",
            "interactionCount": 1,
            "durationMs": 3000,
        },
        received_ts="2026-03-26T16:43:50+00:00",
        payload_json='{"event":"session_ended","deviceId":"bb-123","sessionId":"missing-session","timestamp":"20260326164350","interactionCount":1,"durationMs":3000}',
    )

    session = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        ("missing-session",),
    ).fetchone()
    event = conn.execute(
        "SELECT * FROM events WHERE session_id = ? AND event_type = ?",
        ("missing-session", "session_ended"),
    ).fetchone()

    assert session is None
    assert event is None


def test_handle_session_ended_ignores_duplicate_end(conn):
    handle_session_started(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_started",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164347",
        },
        received_ts="2026-03-26T16:43:47+00:00",
        payload_json='{"event":"session_started","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164347"}',
    )

    handle_session_ended(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_ended",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164350",
            "interactionCount": 1,
            "durationMs": 3000,
        },
        received_ts="2026-03-26T16:43:50+00:00",
        payload_json='{"event":"session_ended","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164350","interactionCount":1,"durationMs":3000}',
    )

    handle_session_ended(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_ended",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164355",
            "interactionCount": 2,
            "durationMs": 5000,
        },
        received_ts="2026-03-26T16:43:55+00:00",
        payload_json='{"event":"session_ended","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164355","interactionCount":2,"durationMs":5000}',
    )

    events = conn.execute(
        "SELECT * FROM events WHERE session_id = ? AND event_type = ?",
        ("sess-1", "session_ended"),
    ).fetchall()
    session = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        ("sess-1",),
    ).fetchone()

    assert len(events) == 1
    assert session["duration_ms"] == 3000
    assert session["interaction_count"] == 1


def test_handle_switch_changed_ignores_ended_session(conn):
    handle_session_started(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_started",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164347",
        },
        received_ts="2026-03-26T16:43:47+00:00",
        payload_json='{"event":"session_started","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164347"}',
    )

    handle_session_ended(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_ended",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164350",
            "interactionCount": 0,
            "durationMs": 3000,
        },
        received_ts="2026-03-26T16:43:50+00:00",
        payload_json='{"event":"session_ended","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164350","interactionCount":0,"durationMs":3000}',
    )

    handle_switch_changed(
        topic="busyboard/bb-123/switch/SW1",
        data={
            "event": "switch_changed",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "switch": "SW1",
            "value": 1,
            "timestamp": "20260326164352",
        },
        received_ts="2026-03-26T16:43:52+00:00",
        payload_json='{"event":"switch_changed","deviceId":"bb-123","sessionId":"sess-1","switch":"SW1","value":1,"timestamp":"20260326164352"}',
    )

    switch_events = conn.execute(
        "SELECT * FROM switch_events WHERE session_id = ?",
        ("sess-1",),
    ).fetchall()
    session = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        ("sess-1",),
    ).fetchone()

    assert len(switch_events) == 0
    assert session["interaction_count"] == 0


def test_handle_session_started_ignores_already_ended_session(conn):
    handle_session_started(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_started",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164347",
        },
        received_ts="2026-03-26T16:43:47+00:00",
        payload_json='{"event":"session_started","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164347"}',
    )

    handle_session_ended(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_ended",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164350",
            "interactionCount": 0,
            "durationMs": 3000,
        },
        received_ts="2026-03-26T16:43:50+00:00",
        payload_json='{"event":"session_ended","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164350","interactionCount":0,"durationMs":3000}',
    )

    handle_session_started(
        topic="busyboard/bb-123/events",
        data={
            "event": "session_started",
            "deviceId": "bb-123",
            "sessionId": "sess-1",
            "timestamp": "20260326164355",
        },
        received_ts="2026-03-26T16:43:55+00:00",
        payload_json='{"event":"session_started","deviceId":"bb-123","sessionId":"sess-1","timestamp":"20260326164355"}',
    )

    events = conn.execute(
        "SELECT * FROM events WHERE session_id = ? AND event_type = ?",
        ("sess-1", "session_started"),
    ).fetchall()
    session = conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?",
        ("sess-1",),
    ).fetchone()

    assert len(events) == 1
    assert session["status"] == "ended"