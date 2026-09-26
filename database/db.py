import sqlite3
import os
from pathlib import Path
from flask import current_app, g

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent.parent

def is_postgres_url(url: str) -> bool:
    """Check if the provided target path or URL is a PostgreSQL / Supabase connection string."""
    if not url or not isinstance(url, str):
        return False
    return url.startswith("postgres://") or url.startswith("postgresql://")

def get_db_path():
    """Return the database path/URL from Flask app config, env, or default SQLite."""
    # Check DATABASE_URL first (standard for Supabase / Heroku / Render / Cloud)
    db_url = os.environ.get("DATABASE_URL")
    if db_url and is_postgres_url(db_url):
        return db_url

    if current_app:
        cfg_path = current_app.config.get("DATABASE_PATH")
        if cfg_path:
            if not is_postgres_url(cfg_path) and cfg_path != ":memory:":
                p = Path(cfg_path)
                return str(p if p.is_absolute() else BASE_DIR / p)
            return cfg_path

    env_path = os.environ.get("DATABASE_PATH", str(BASE_DIR / "database" / "scholarships.db"))
    if not is_postgres_url(env_path) and env_path != ":memory:":
        p = Path(env_path)
        return str(p if p.is_absolute() else BASE_DIR / p)
    return env_path

def get_db(db_path=None):
    """Retrieve or create an active database connection for the request context."""
    target = db_path or get_db_path()
    
    if current_app and "db" in g and db_path is None:
        return g.db

    # 1. PostgreSQL / Supabase Connection
    if is_postgres_url(target):
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2 is required to connect to PostgreSQL/Supabase. Run: pip install psycopg2-binary")
        
        # PostgreSQL connections require 'postgresql://' scheme
        clean_url = target.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(clean_url, cursor_factory=RealDictCursor)
        conn.autocommit = False
        if current_app and db_path is None:
            g.db = conn
            g.is_postgres = True
        return conn

    # 2. SQLite Connection (Local & Testing)
    if target != ":memory:" and not os.path.exists(target):
        init_db(target)

    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    if target == ":memory:":
        schema_path = BASE_DIR / "database" / "schema.sql"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
    
    if current_app and db_path is None:
        g.db = conn
        g.is_postgres = False
    return conn

def close_db(e=None):
    """Close the database connection if open."""
    db = g.pop("db", None) if current_app else None
    if db is not None:
        db.close()

def init_db(db_path=None, schema_path=None):
    """Initialize database tables using schema.sql (SQLite) or supabase_schema.sql (Postgres)."""
    target = db_path or get_db_path()

    if is_postgres_url(target):
        if schema_path is None:
            schema_path = BASE_DIR / "database" / "supabase_schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        clean_url = target.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(clean_url)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.close()
        return

    # SQLite initialization
    if target != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)





    if schema_path is None:
        schema_path = BASE_DIR / "database" / "schema.sql"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(target)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False, db_path=None):
    """Helper to query database safely with parameter substitution across SQLite and PostgreSQL."""
    target = db_path or get_db_path()
    is_pg = is_postgres_url(target)
    is_standalone = (db_path is not None or not current_app)
    conn = get_db(db_path)

    try:
        if is_pg:
            # Translate '?' placeholders to '%s' for PostgreSQL
            pg_query = query.replace("?", "%s")
            cur = conn.cursor()
            cur.execute(pg_query, args)
            rv = cur.fetchall()
            cur.close()
            return (dict(rv[0]) if rv else None) if one else [dict(r) for r in rv]
        else:
            cur = conn.execute(query, args)
            rv = cur.fetchall()
            cur.close()
            return (dict(rv[0]) if rv else None) if one else [dict(r) for r in rv]
    finally:
        if is_standalone and conn:
            conn.close()

def execute_db(query, args=(), db_path=None):
    """Helper to execute write commands (INSERT, UPDATE, DELETE) returning last generated ID."""
    target = db_path or get_db_path()
    is_pg = is_postgres_url(target)
    conn = get_db(db_path)
    cur = conn.cursor()

    if is_pg:
        pg_query = query.replace("?", "%s")
        is_insert = pg_query.strip().upper().startswith("INSERT")
        if is_insert and "RETURNING" not in pg_query.upper():
            pg_query = pg_query.rstrip(" ;") + " RETURNING id;"

        cur.execute(pg_query, args)
        conn.commit()
        last_id = None
        if is_insert:
            row = cur.fetchone()
            if row:
                last_id = row["id"] if isinstance(row, dict) else row[0]
        cur.close()
        return last_id
    else:
        cur.execute(query, args)
        conn.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id
