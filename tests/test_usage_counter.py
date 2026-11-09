import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime, timezone
from contextlib import closing

from usage_counter import get_usage_count, get_usage_stats


class UsageCounterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "data" / "usage.sqlite3"

    def count(self, session_id=None):
        return get_usage_count(session_id, database_path=self.database)

    def test_read_only_visits_do_not_increment(self):
        self.assertEqual(self.count(), 0)
        self.assertEqual(self.count(), 0)

    def test_session_is_counted_once_and_saved_between_connections(self):
        self.assertEqual(self.count("session-a"), 1)
        self.assertEqual(self.count("session-a"), 1)
        self.assertEqual(self.count("session-b"), 2)
        self.assertEqual(self.count(), 2)
        self.assertEqual(self.count("session-a"), 2)

    def test_concurrent_sessions_and_retries_do_not_lose_or_duplicate_counts(self):
        session_ids = [f"session-{index}" for index in range(24)] * 3
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(self.count, session_ids))
        self.assertEqual(self.count(), 24)

    def test_session_id_is_stored_as_data(self):
        value = "'); DROP TABLE usage_sessions; --"
        self.assertEqual(self.count(value), 1)
        self.assertEqual(self.count(value), 1)
        self.assertEqual(self.count("another-session"), 2)

    def test_invalid_session_ids_are_rejected(self):
        for value in ("", " ", 1, False):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.count(value)

    def test_database_failure_does_not_report_a_false_zero(self):
        self.database.parent.mkdir(parents=True)
        self.database.write_text("invalid database", encoding="utf-8")
        with self.assertRaises(sqlite3.DatabaseError):
            self.count()

    def test_daily_count_rolls_over_without_counting_same_session_again(self):
        before_midnight = datetime(2026, 11, 7, 15, 59, tzinfo=timezone.utc)
        midnight = datetime(2026, 11, 7, 16, 0, tzinfo=timezone.utc)
        self.assertEqual(get_usage_stats("first", database_path=self.database, now=before_midnight), {"total": 1, "today": 1})
        self.assertEqual(get_usage_stats("first", database_path=self.database, now=midnight), {"total": 1, "today": 0})
        self.assertEqual(get_usage_stats("second", database_path=self.database, now=midnight), {"total": 2, "today": 1})

    def test_legacy_database_is_migrated_without_guessing_dates(self):
        self.database.parent.mkdir(parents=True)
        with closing(sqlite3.connect(self.database)) as connection:
            with connection:
                connection.execute("CREATE TABLE usage_sessions (session_id TEXT PRIMARY KEY NOT NULL)")
                connection.execute("INSERT INTO usage_sessions VALUES ('legacy')")
        self.assertEqual(get_usage_stats("legacy", database_path=self.database), {"total": 1, "today": 0})
        self.assertEqual(get_usage_stats("new", database_path=self.database), {"total": 2, "today": 1})

    def test_delayed_registration_uses_original_login_time(self):
        started_at = datetime(2026, 11, 7, 15, 59, tzinfo=timezone.utc)
        now = datetime(2026, 11, 7, 16, 1, tzinfo=timezone.utc)
        stats = get_usage_stats("delayed", database_path=self.database, started_at=started_at, now=now)
        self.assertEqual(stats, {"total": 1, "today": 0})
        bangkok = get_usage_stats(database_path=self.database, now=now, timezone_name="Asia/Bangkok")
        self.assertEqual(bangkok, {"total": 1, "today": 1})


if __name__ == "__main__":
    unittest.main()
