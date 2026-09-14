"""Real Postgres checks; enable with --postgres against the disposable fixture."""

from datetime import datetime, timezone

import psycopg2
import pytest

import handlers
import supabase_repositories as sr

pytestmark = pytest.mark.postgres
TS = "2026-09-09T12:00:00+00:00"
SID = "20260909120000"


def rows(conn, query, args=()):
    with conn.cursor() as cur:
        cur.execute(query, args)
        return cur.fetchall()


def seed(conn):
    sr.upsert_device(conn=conn, device_id="bb-test", seen_ts=TS, status="online")
    sr.create_session_if_missing(conn=conn, session_id=SID, device_id="bb-test", started_at=TS)


def test_device_upsert_preserves_first_seen_and_updates_presence(pg_conn):
    sr.upsert_device(conn=pg_conn, device_id="bb-test", seen_ts=TS, status="online")
    sr.upsert_device(conn=pg_conn, device_id="bb-test", seen_ts="2026-09-09T12:00:05Z", status="offline")
    device = rows(pg_conn, "SELECT * FROM devices")[0]
    assert device["first_seen_at"] == datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
    assert device["last_seen_at"] == datetime(2026, 9, 9, 12, 0, 5, tzinfo=timezone.utc)
    assert device["status"] == "offline"


def test_session_create_and_end_guards_preserve_final_values(pg_conn):
    seed(pg_conn)
    sr.increment_session_interaction_count(conn=pg_conn, session_id=SID)
    sr.create_session_if_missing(conn=pg_conn, session_id=SID, device_id="bb-test", started_at=TS)
    assert rows(pg_conn, "SELECT interaction_count FROM sessions")[0]["interaction_count"] == 1
    sr.end_session(conn=pg_conn, session_id=SID, ended_at=TS, duration_ms=5000, interaction_count=7)
    sr.increment_session_interaction_count(conn=pg_conn, session_id=SID)
    sr.end_session(conn=pg_conn, session_id=SID, ended_at=TS, duration_ms=9999, interaction_count=99)
    sr.create_session_if_missing(conn=pg_conn, session_id=SID, device_id="bb-test", started_at=TS)
    sr.end_session(conn=pg_conn, session_id="missing", ended_at=TS, duration_ms=1, interaction_count=0)
    session = rows(pg_conn, "SELECT * FROM sessions")[0]
    assert session["status"] == "ended"
    assert session["interaction_count"] == 7
    assert session["duration_ms"] == 5000


def test_event_json_and_cloud_switch_projection(pg_conn):
    seed(pg_conn)
    for _ in range(2):
        sr.insert_event(
            conn=pg_conn, device_id="bb-test", session_id=SID, event_type="switch_changed",
            event_ts=TS, received_ts=TS, topic="busyboard/bb-test/switch/SW1",
            payload_json='{"switch":"SW1","value":1}',
        )
        sr.insert_switch_event(
            conn=pg_conn, session_id=SID, device_id="bb-test", switch_name="SW1", value=1, event_ts=TS
        )
    events = rows(pg_conn, "SELECT * FROM events ORDER BY id")
    switches = rows(pg_conn, "SELECT * FROM switch_events ORDER BY id")
    assert len(events) == len(switches) == 2  # Current inserts do not deduplicate.
    assert events[0]["id"] != events[1]["id"]
    assert events[0]["payload_json"] == {"switch": "SW1", "value": 1}
    assert switches[0]["value"] == 1
    assert "event_id" not in switches[0]


def test_repository_commit_and_rollback_are_owned_by_caller(pg_conn, pg_connect):
    observer = pg_connect()
    seed(pg_conn)
    assert rows(observer, "SELECT * FROM devices") == []
    pg_conn.commit()
    assert len(rows(observer, "SELECT * FROM devices")) == 1
    sr.upsert_device(conn=pg_conn, device_id="bb-test", seen_ts=TS, status="offline")
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        sr.insert_switch_event(
            conn=pg_conn, session_id="missing", device_id="bb-test", switch_name="SW1", value=1, event_ts=TS
        )
    pg_conn.rollback()
    assert rows(observer, "SELECT status FROM devices")[0]["status"] == "online"
    assert rows(observer, "SELECT * FROM switch_events") == []


def test_handler_lifecycle_reaches_cloud_and_dashboard_fields(
    conn, pg_conn, pg_connect, emit, cloud_jobs, run_cloud_worker
):
    emit("device_connected")
    emit("session_started")
    emit("switch_changed")
    handlers.handle_device_offline(device_id="bb-test", received_ts=TS)
    run_cloud_worker(cloud_jobs, pg_connect)
    assert rows(pg_conn, "SELECT status FROM devices")[0]["status"] == "offline"
    assert rows(pg_conn, "SELECT status FROM sessions")[0]["status"] == "active"

    cloud_jobs.clear()
    handlers.handle_device_online(device_id="bb-test", received_ts=TS)
    emit("session_ended")
    run_cloud_worker(cloud_jobs, pg_connect)
    session = rows(pg_conn, """
        SELECT s.session_id, s.device_id, s.started_at, s.ended_at,
               s.duration_ms, s.interaction_count, s.status,
               (SELECT COUNT(DISTINCT switch_name) FROM switch_events e
                WHERE e.session_id = s.session_id) AS switch_count
        FROM sessions s WHERE s.session_id = %s
    """, (SID,))[0]
    assert session["session_id"] == SID
    assert session["device_id"] == "bb-test"
    assert session["started_at"] == datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
    assert session["ended_at"] == datetime(2026, 9, 9, 12, 0, 5, tzinfo=timezone.utc)
    assert session["status"] == "ended"
    assert session["switch_count"] == 1
    assert session["duration_ms"] == 5000
    assert session["interaction_count"] == 7  # Firmware final count wins.
    assert conn.execute("SELECT interaction_count FROM sessions").fetchone()[0] == 7
    audit = rows(pg_conn, """
        SELECT id, event_type, event_ts, device_id, payload_json FROM events
        WHERE session_id = %s AND event_type IN ('session_started', 'session_ended')
        ORDER BY event_ts DESC
    """, (SID,))
    assert [row["event_type"] for row in audit] == ["session_ended", "session_started"]
    assert audit[0]["payload_json"]["interactionCount"] == 7
    assert len(rows(pg_conn, "SELECT id, switch_name, value, event_ts FROM switch_events WHERE session_id = %s", (SID,))) == 1
    assert rows(pg_conn, "SELECT status FROM devices")[0]["status"] == "online"


def test_cloud_parent_loss_causes_later_switch_job_to_fail(
    conn, pg_conn, pg_connect, emit, cloud_jobs, run_cloud_worker, caplog
):
    emit("session_started")
    emit("switch_changed")
    # Simulate the earlier session-start job having been dropped. The switch
    # handler uses local presence of the session to omit its cloud creation.
    run_cloud_worker(cloud_jobs[1:], pg_connect)
    assert rows(pg_conn, "SELECT * FROM devices") == []  # Partial upsert rolled back.
    assert rows(pg_conn, "SELECT * FROM events") == []
    assert rows(pg_conn, "SELECT * FROM switch_events") == []
    assert conn.execute("SELECT interaction_count FROM sessions").fetchone()[0] == 1
    assert "Supabase write failed" in caplog.text


def test_switch_first_synthesizes_session_in_both_stores(
    conn, pg_conn, pg_connect, emit, cloud_jobs, run_cloud_worker
):
    emit("switch_changed")
    run_cloud_worker(cloud_jobs, pg_connect)
    session = rows(pg_conn, "SELECT * FROM sessions")[0]
    assert session["status"] == "active"
    assert session["interaction_count"] == 1
    assert conn.execute("SELECT interaction_count FROM sessions").fetchone()[0] == 1


def test_replaying_current_cloud_closure_duplicates_rows_and_counts(
    pg_conn, pg_connect, emit, cloud_jobs, run_cloud_worker
):
    emit("switch_changed")
    run_cloud_worker([cloud_jobs[0], cloud_jobs[0]], pg_connect)
    assert len(rows(pg_conn, "SELECT * FROM events")) == 2
    assert len(rows(pg_conn, "SELECT * FROM switch_events")) == 2
    assert rows(pg_conn, "SELECT interaction_count FROM sessions")[0]["interaction_count"] == 2
