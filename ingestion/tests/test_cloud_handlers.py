"""Local/cloud boundary tests for the current handler implementation."""

from unittest.mock import Mock

import pytest

import cloud_publisher
import db
import handlers
import supabase_repositories as sr


def test_cloud_work_is_enqueued_only_after_local_commit(monkeypatch, emit):
    seen = []

    def enqueue(job):
        connection = db.get_connection()
        try:
            # An independent reader must observe the complete committed write.
            row = connection.execute("SELECT interaction_count FROM sessions").fetchone()
            seen.append(row["interaction_count"])
            assert connection.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 1
            assert connection.execute("SELECT COUNT(*) FROM switch_events").fetchone()[0] == 1
        finally:
            connection.close()

    monkeypatch.setattr(cloud_publisher, "enqueue", enqueue)
    emit("switch_changed")
    assert seen == [1]


def test_local_failure_rolls_back_and_does_not_enqueue(monkeypatch, conn, emit, cloud_jobs):
    monkeypatch.setattr(handlers, "insert_switch_event", Mock(side_effect=RuntimeError("test failure")))
    with pytest.raises(RuntimeError, match="test failure"):
        emit("switch_changed")
    for table in ("devices", "sessions", "events", "switch_events"):
        assert conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
    assert cloud_jobs == []


def test_cloud_failure_does_not_undo_committed_local_state(
    monkeypatch, conn, emit, cloud_jobs, run_cloud_worker
):
    emit("switch_changed")
    monkeypatch.setattr(sr, "upsert_device", Mock(side_effect=RuntimeError("cloud outage")))
    connection = Mock(closed=0)
    run_cloud_worker(cloud_jobs, lambda: connection)
    assert conn.execute("SELECT interaction_count FROM sessions").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM switch_events").fetchone()[0] == 1
    connection.rollback.assert_called_once_with()


@pytest.mark.parametrize("event", ["session_started", "switch_changed", "session_ended"])
def test_ignored_ended_session_updates_local_presence_without_cloud_job(
    event, conn, emit, cloud_jobs
):
    emit("session_started")
    emit("session_ended")
    handlers.handle_device_offline(device_id="bb-test", received_ts="2026-09-09T12:00:06+00:00")
    cloud_jobs.clear()
    before = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    emit(event, timestamp="20260909120007")
    assert conn.execute("SELECT status FROM devices").fetchone()[0] == "online"
    assert conn.execute("SELECT status FROM sessions").fetchone()[0] == "ended"
    assert conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] == before
    assert cloud_jobs == []


def test_unknown_end_updates_only_local_presence(conn, emit, cloud_jobs):
    emit("session_ended")
    assert conn.execute("SELECT status FROM devices").fetchone()[0] == "online"
    assert conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 0
    assert cloud_jobs == []


def test_duplicate_switch_receipts_are_currently_distinct_work(conn, emit, cloud_jobs):
    emit("switch_changed")
    emit("switch_changed")
    assert conn.execute("SELECT interaction_count FROM sessions").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM switch_events").fetchone()[0] == 2
    assert len(cloud_jobs) == 2
