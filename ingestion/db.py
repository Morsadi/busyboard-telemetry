import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "busyboard.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def init_db() -> None:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    with get_connection() as conn:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema)


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")