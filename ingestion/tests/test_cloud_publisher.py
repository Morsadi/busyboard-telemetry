"""Characterize current best-effort delivery, including its known loss cases."""

from unittest.mock import Mock

import pytest

import cloud_publisher
import config
import supabase_db


def test_unconfigured_start_drops_enqueued_work(monkeypatch, caplog):
    connect = Mock()
    thread = Mock()
    monkeypatch.setattr(supabase_db, "get_connection", connect)
    monkeypatch.setattr(cloud_publisher.threading, "Thread", thread)
    cloud_publisher.start()
    cloud_publisher.enqueue(Mock())
    assert not cloud_publisher._enabled
    assert cloud_publisher._queue.empty()
    connect.assert_not_called()
    thread.assert_not_called()
    assert "cloud sync disabled" in caplog.text


def test_failed_startup_probe_keeps_delivery_disabled(monkeypatch, caplog):
    monkeypatch.setattr(config, "SUPABASE_DB_URL", "test-configuration")
    connect = Mock(side_effect=ConnectionError("test outage"))
    thread = Mock()
    monkeypatch.setattr(supabase_db, "get_connection", connect)
    monkeypatch.setattr(cloud_publisher.threading, "Thread", thread)
    cloud_publisher.start()
    connect.side_effect = None
    cloud_publisher.enqueue(Mock())
    assert not cloud_publisher._enabled
    assert cloud_publisher._queue.empty()
    connect.assert_called_once_with()
    thread.assert_not_called()
    assert "local-only mode" in caplog.text


def test_successful_probe_closes_probe_and_starts_worker(monkeypatch):
    monkeypatch.setattr(config, "SUPABASE_DB_URL", "test-configuration")
    probe = Mock()
    thread = Mock()
    monkeypatch.setattr(supabase_db, "get_connection", Mock(return_value=probe))
    monkeypatch.setattr(cloud_publisher.threading, "Thread", thread)
    cloud_publisher.start()
    probe.close.assert_called_once_with()
    thread.assert_called_once_with(
        target=cloud_publisher._worker, daemon=True, name="supabase-publisher"
    )
    thread.return_value.start.assert_called_once_with()
    job = Mock()
    cloud_publisher.enqueue(job)
    assert cloud_publisher._queue.get_nowait() is job
    job.assert_not_called()


def test_worker_preserves_order_and_commits_each_job(run_cloud_worker):
    calls = []
    connection = Mock(closed=0)
    connection.commit.side_effect = lambda: calls.append("commit")
    connect = Mock(return_value=connection)

    def first(conn):
        assert conn is connection
        calls.append("first")

    def second(conn):
        assert conn is connection
        calls.append("second")

    run_cloud_worker([first, second], connect)
    assert calls == ["first", "commit", "second", "commit"]
    connect.assert_called_once_with()
    connection.rollback.assert_not_called()


@pytest.mark.parametrize("failure", ["connect", "write", "commit", "rollback", "close"])
def test_failed_job_is_dropped_and_next_job_reconnects(failure, run_cloud_worker, caplog):
    bad = Mock(closed=0)
    good = Mock(closed=0)
    failed_job = Mock()
    next_job = Mock()
    if failure == "connect":
        connect = Mock(side_effect=[ConnectionError("test outage"), good])
    else:
        connect = Mock(side_effect=[bad, good])
        if failure == "commit":
            bad.commit.side_effect = RuntimeError("test commit failure")
        else:
            failed_job.side_effect = RuntimeError("test write failure")
        if failure in ("rollback", "close"):
            getattr(bad, failure).side_effect = RuntimeError("test cleanup failure")

    run_cloud_worker([failed_job, next_job], connect)
    assert connect.call_count == 2
    assert failed_job.call_count == (0 if failure == "connect" else 1)
    next_job.assert_called_once_with(good)
    good.commit.assert_called_once_with()
    if failure != "connect":
        bad.rollback.assert_called_once_with()
        bad.close.assert_called_once_with()
    assert "Supabase write failed" in caplog.text


def test_closed_connection_is_replaced_before_next_job(run_cloud_worker):
    first = Mock(closed=0)
    second = Mock(closed=0)

    def close_after_commit():
        first.closed = 1

    first.commit.side_effect = close_after_commit
    job = Mock()
    connect = Mock(side_effect=[first, second])
    run_cloud_worker([Mock(), job], connect)
    job.assert_called_once_with(second)
    assert connect.call_count == 2
