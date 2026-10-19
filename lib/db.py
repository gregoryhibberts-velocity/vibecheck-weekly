"""Postgres when DATABASE_URL is set (Neon in production on Render); SQLite fallback for local dev."""
import sqlite3, time
from . import config
PG = bool(config.DATABASE_URL and config.DATABASE_URL.startswith("postgres"))
SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts(id {pk}, email TEXT UNIQUE NOT NULL, plan TEXT DEFAULT 'free',
  stripe_customer TEXT, stripe_subscription TEXT, created_at BIGINT);
CREATE TABLE IF NOT EXISTS sites(id {pk}, account_id INTEGER NOT NULL, url TEXT NOT NULL, host TEXT NOT NULL,
  verify_token TEXT NOT NULL, manage_key TEXT UNIQUE NOT NULL, verified_at BIGINT, weekly INTEGER DEFAULT 0, created_at BIGINT);
CREATE TABLE IF NOT EXISTS scans(id {pk}, token TEXT UNIQUE NOT NULL, site_id INTEGER, url TEXT, email TEXT,
  unlocked INTEGER DEFAULT 0, status TEXT, score INTEGER, result TEXT, created_at BIGINT);
CREATE TABLE IF NOT EXISTS rate_events(id {pk}, k TEXT NOT NULL, ts BIGINT NOT NULL);
CREATE INDEX IF NOT EXISTS rate_k_ts ON rate_events(k, ts);
"""
_conn = None
def conn():
    global _conn
    if _conn is None:
        if PG:
            import psycopg
            from psycopg.rows import dict_row
            _conn = psycopg.connect(config.DATABASE_URL, autocommit=True, row_factory=dict_row)
            for stmt in SCHEMA.format(pk="SERIAL PRIMARY KEY").split(";"):
                if stmt.strip(): _conn.execute(stmt)
        else:
            _conn = sqlite3.connect(config.SQLITE_PATH, check_same_thread=False, isolation_level=None)
            _conn.row_factory = lambda c, r: {d[0]: r[i] for i, d in enumerate(c.description)}
            _conn.executescript(SCHEMA.format(pk="INTEGER PRIMARY KEY AUTOINCREMENT"))
    return _conn
import threading
_lock = threading.Lock()
def q(sql, args=()):
    global _conn
    if PG: sql = sql.replace("?", "%s")
    with _lock:
        try: return _FakeCur(conn().execute(sql, args))
        except Exception as e:
            if not PG or "OperationalError" not in type(e).__name__ and "closed" not in str(e).lower(): raise
            _conn = None  # Neon closes idle connections; reconnect once
            return _FakeCur(conn().execute(sql, args))
class _FakeCur:
    """Fetch results while holding the lock so threads never share a live cursor."""
    def __init__(self, cur):
        try: self.rows = cur.fetchall() if cur.description else []
        except Exception: self.rows = []
    def fetchone(self): return self.rows[0] if self.rows else None
    def fetchall(self): return self.rows
def one(sql, args=()): return q(sql, args).fetchone()
def all(sql, args=()): return q(sql, args).fetchall()
def insert(sql, args=()): return q(sql + " RETURNING id", args).fetchone()["id"]
def now(): return int(time.time())
