import psycopg2
import psycopg2.extras

from config import SUPABASE_DB_URL


def get_connection() -> psycopg2.extensions.connection:
    """
    Open a new psycopg2 connection to Supabase.
    The caller is responsible for closing it.
    Uses RealDictCursor so rows behave like dicts, matching the sqlite3.Row
    pattern used throughout the rest of the codebase.
    """
    conn = psycopg2.connect(
        SUPABASE_DB_URL,
        cursor_factory=psycopg2.extras.RealDictCursor,
        connect_timeout=5,
    )
    return conn
