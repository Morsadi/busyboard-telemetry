import queue
import sys
from pathlib import Path

import dotenv
import psycopg2
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
