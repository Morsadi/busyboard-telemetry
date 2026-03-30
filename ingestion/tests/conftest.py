import pytest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
import db


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