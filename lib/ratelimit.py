from . import db
def hit(key, limit, window_s):
    """Record an event and return True if still within limit."""
    t = db.now()
    db.q("DELETE FROM rate_events WHERE ts < ?", (t - 86400 * 2,))
    n = db.one("SELECT COUNT(*) AS n FROM rate_events WHERE k=? AND ts>?", (key, t - window_s))["n"]
    if n >= limit: return False
    db.q("INSERT INTO rate_events(k, ts) VALUES(?, ?)", (key, t)); return True
