"""
cloud_publisher.py

Manages a background daemon thread that drains a queue of Supabase write
functions. MQTT message processing is never blocked — if Supabase is slow
or unavailable, the local SQLite write has already committed and the queue
entry is simply logged and dropped.

Usage
-----
    # In app.py, before the MQTT loop:
    cloud_publisher.start()

    # In any handler, after conn.commit():
    cloud_publisher.enqueue(some_callable_that_accepts_a_psycopg2_conn)
"""

import logging
import queue
import threading
from typing import Callable

import psycopg2

logger = logging.getLogger(__name__)

# Each item on the queue is a callable (conn) -> None.
_queue: queue.Queue[Callable] = queue.Queue()
_enabled = False


def enqueue(fn: Callable) -> None:
    """
    Queue a Supabase write. No-op (and zero overhead) if the cloud
    publisher failed to start (e.g. no SUPABASE_DB_URL configured,
    or Supabase unreachable at startup).
    """
    if _enabled:
        _queue.put(fn)


def _worker() -> None:
    """
    Background worker thread. Maintains a single persistent
    psycopg2 connection and reconnects automatically on failure so that
    transient network hiccups don't require a restart.
    """
    from supabase_db import get_connection

    conn: psycopg2.extensions.connection | None = None

    while True:
        fn = _queue.get()
        try:
            # Reconnect if the connection was lost or never opened.
            if conn is None or conn.closed:
                logger.info("cloud_publisher | opening Supabase connection")
                conn = get_connection()

            fn(conn)
            conn.commit()

        except Exception:
            logger.exception("cloud_publisher | Supabase write failed — skipping")

            # Roll back any partial work and drop the connection so the
            # next iteration opens a fresh one.
            if conn is not None and not conn.closed:
                try:
                    conn.rollback()
                except Exception:
                    pass
                try:
                    conn.close()
                except Exception:
                    pass
            conn = None

        finally:
            _queue.task_done()


def start() -> None:
    """
    Probe Supabase and, if reachable, start the background worker thread.
    Logs a warning (but does NOT raise) if Supabase is unavailable so the
    ingestion service continues running in local-only mode.
    """
    global _enabled

    from config import SUPABASE_DB_URL

    if not SUPABASE_DB_URL:
        logger.warning(
            "cloud_publisher | SUPABASE_DB_URL not set — cloud sync disabled"
        )
        return

    try:
        from supabase_db import get_connection

        probe = get_connection()
        probe.close()
    except Exception as exc:
        logger.warning(
            "cloud_publisher | Supabase not reachable (%s) — running in local-only mode",
            exc,
        )
        return

    _enabled = True
    thread = threading.Thread(target=_worker, daemon=True, name="supabase-publisher")
    thread.start()
    logger.info("cloud_publisher | started — dual-write to Supabase enabled")
