import json
import os
import queue
import sys
from pathlib import Path
from uuid import uuid4

import dotenv
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Configure application imports before collection, when autouse fixtures cannot
# yet protect config.py's import-time dotenv loading.
with pytest.MonkeyPatch.context() as isolation:
    isolation.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    for name in ("MQTT_USER", "MQTT_PASSWORD", "SUPABASE_DB_URL"):
        isolation.setenv(name, "")
    import config
    import supabase_db

import db
import cloud_publisher

_postgres_connect = psycopg2.connect


def pytest_addoption(parser):
    parser.addoption("--postgres", action="store_true", help="Run disposable local Postgres tests")
    parser.addoption("--postgres-port", type=int, default=55432, help="Local test Postgres port")


def pytest_configure(config):
    config.addinivalue_line("markers", "postgres: requires an explicitly enabled local test Postgres")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--postgres"):
        skip = pytest.mark.skip(reason="Use --postgres to run disposable Postgres integration tests")
        for item in items:
            if "postgres" in item.keywords:
                item.add_marker(skip)


@pytest.fixture(autouse=True)
def isolated_runtime(monkeypatch, test_db):
    def forbidden_connection(*args, **kwargs):
        raise AssertionError("Use a fake connection or the explicit pg_connect fixture")

    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    for name in ("MQTT_USER", "MQTT_PASSWORD", "SUPABASE_DB_URL"):
        monkeypatch.setenv(name, "")
        monkeypatch.setattr(config, name, "")
    monkeypatch.setattr(supabase_db, "SUPABASE_DB_URL", "")
    monkeypatch.setattr(psycopg2, "connect", forbidden_connection)
    monkeypatch.setattr(cloud_publisher, "_enabled", False)
    monkeypatch.setattr(cloud_publisher, "_queue", queue.Queue())


@pytest.fixture
def cloud_jobs(monkeypatch):
    jobs = []
    monkeypatch.setattr(cloud_publisher, "enqueue", jobs.append)
    return jobs


@pytest.fixture
def emit():
    from router import handle_message

    def send(event, **changes):
        data = dict(
            event=event, deviceId="bb-test", sessionId="20260909120000",
            timestamp="20260909120000",
        )
        if event == "switch_changed":
            data.update(switch="SW1", value=1)
        if event == "session_ended":
            data.update(interactionCount=7, durationMs=5000, timestamp="20260909120005")
        data.update(changes)
        topic = "busyboard/" + data["deviceId"]
        topic += "/switch/" + data["switch"] if event == "switch_changed" else "/events"
        handle_message(topic, json.dumps(data).encode())

    return send


@pytest.fixture
def run_cloud_worker(monkeypatch):
    # The current worker has no stop API. End only when it asks for the next
    # item after the finite queue is exhausted, outside its exception handler.
    class QueueDrained(BaseException):
        pass

    def run(jobs, get_connection):
        work = queue.Queue()
        for job in jobs:
            work.put(job)
        original_get = work.get

        def get_next():
            try:
                return original_get(block=False)
            except queue.Empty:
                raise QueueDrained() from None

        monkeypatch.setattr(work, "get", get_next)
        monkeypatch.setattr(cloud_publisher, "_queue", work)
        monkeypatch.setattr(supabase_db, "get_connection", get_connection)
        with pytest.raises(QueueDrained):
            cloud_publisher._worker()
        assert work.unfinished_tasks == 0

    return run


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_busyboard.db"
    schema_path = tmp_path / "schema.sql"

    schema_text = db.SCHEMA_PATH.read_text(encoding="utf-8")
    schema_path.write_text(schema_text, encoding="utf-8")

    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(db, "SCHEMA_PATH", schema_path)

    db.init_db()
    return db_path


@pytest.fixture
def conn(test_db):
    connection = db.get_connection()
    yield connection
    connection.close()


@pytest.fixture
def pg_connect(request, monkeypatch):
    """Only the explicit, loopback-only disposable database can be used here."""
    if not request.config.getoption("--postgres"):
        pytest.skip("Use --postgres to enable the disposable database")
    port = request.config.getoption("--postgres-port")
    if not 1024 <= port <= 65535:
        pytest.fail("--postgres-port must be between 1024 and 65535", pytrace=False)

    # Do not inherit libpq services, passwords, options, or credential files.
    for name in tuple(os.environ):
        if name.startswith("PG"):
            monkeypatch.delenv(name)
    settings = dict(
        host="127.0.0.1", port=port, dbname="busyboard_test", user="busyboard_test",
        password="", passfile=os.devnull, connect_timeout=3,
        options="-c statement_timeout=5000 -c lock_timeout=2000",
        cursor_factory=RealDictCursor,
    )
    try:
        admin = _postgres_connect(**settings)
    except psycopg2.Error:
        admin = None
    if admin is None:
        pytest.fail("Disposable Postgres unavailable; follow docs/testing.md setup", pytrace=False)
    admin.autocommit = True
    schema = "busyboard_test_" + uuid4().hex
    connections = []
    created = False
    try:
        with admin.cursor() as cur:
            cur.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        created = True

        def connect():
            connection = _postgres_connect(**settings)
            connections.append(connection)
            with connection.cursor() as cur:
                cur.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
            connection.commit()
            return connection

        setup = connect()
        # Test fixture only: executable evidence for repository SQL, not a
        # production schema/migration or a copy of local deployment settings.
        from postgres_schema import POSTGRES_SCHEMA
        with setup:
            with setup.cursor() as cur:
                cur.execute(POSTGRES_SCHEMA)
        yield connect
    finally:
        for connection in connections:
            connection.close()
        try:
            if created:
                with admin.cursor() as cur:
                    cur.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
        finally:
            admin.close()


@pytest.fixture
def pg_conn(pg_connect):
    return pg_connect()
