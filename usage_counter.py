"""Count authenticated sessions without storing personal information."""

import sqlite3
from contextlib import closing
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent / "data" / "usage.sqlite3"
DEFAULT_TIMEZONE = "Asia/Shanghai"


def utc_timestamp(value=None):
    value = value or datetime.now(timezone.utc)
    if value.tzinfo is None:
        raise ValueError("Usage timestamps must include a timezone")
    return value.astimezone(timezone.utc)


def day_bounds(now=None, timezone_name=DEFAULT_TIMEZONE):
    zone = ZoneInfo(timezone_name)
    date = utc_timestamp(now).astimezone(zone).date()
    start = datetime.combine(date, time.min, tzinfo=zone)
    end = datetime.combine(date + timedelta(days=1), time.min, tzinfo=zone)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def get_usage_count(session_id=None, *, database_path=None):
    """Compatibility helper for callers that need only the all-time total."""
    return get_usage_stats(session_id, database_path=database_path)["total"]


def get_usage_stats(session_id=None, *, database_path=None, started_at=None,
                    now=None, timezone_name=DEFAULT_TIMEZONE):
    """Register once and return total/today; legacy undated rows count in total."""
    if session_id is not None and (not isinstance(session_id, str) or not session_id.strip()):
        raise ValueError("session_id must be a non-empty string")
    path = Path(database_path) if database_path is not None else DEFAULT_DATABASE_PATH
    start, end = day_bounds(now, timezone_name)
    timestamp = utc_timestamp(started_at or now).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=5)) as connection:
        with connection:
            # Serialize the additive migration along with registration so concurrent
            # requests cannot both attempt to add the timestamp column.
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS usage_sessions "
                "(session_id TEXT PRIMARY KEY NOT NULL, started_at_utc TEXT)"
            )
            columns = {row[1] for row in connection.execute("PRAGMA table_info(usage_sessions)")}
            if "started_at_utc" not in columns:
                connection.execute("ALTER TABLE usage_sessions ADD COLUMN started_at_utc TEXT")
            if session_id is not None:
                connection.execute(
                    "INSERT OR IGNORE INTO usage_sessions (session_id, started_at_utc) VALUES (?, ?)",
                    (session_id, timestamp),
                )
            total, today = connection.execute(
                "SELECT COUNT(*), COALESCE(SUM(started_at_utc >= ? AND started_at_utc < ?), 0) "
                "FROM usage_sessions", (start.isoformat(), end.isoformat())
            ).fetchone()
            return {"total": total, "today": today}
