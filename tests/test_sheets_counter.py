import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import requests

from sheets_counter import GoogleSheetsCounter, SheetsCounterError


class FakeResponse:
    def __init__(self, data, status=200):
        self.data, self.status_code = data, status

    def json(self):
        return self.data


class FakeSheets:
    def __init__(self):
        self.rows = [["session_id", "started_at_utc"]]
        self.calls = []
        self.fail_after_append = False
        self.status = 200
        self.lock = threading.Lock()

    def request(self, method, url, **kwargs):
        with self.lock:
            self.calls.append((method, url, kwargs))
            if self.status != 200:
                return FakeResponse({}, self.status)
            if method == "GET":
                return FakeResponse({"values": [row[:] for row in self.rows]})
            if method == "PUT":
                self.rows[0] = ["session_id", "started_at_utc"]
                return FakeResponse({"updatedCells": 1})
            self.rows.extend(kwargs["json"]["values"])
            if self.fail_after_append:
                self.fail_after_append = False
                raise requests.Timeout("Simulated timeout after commit")
            return FakeResponse({"updates": {"updatedRows": 1}})


class SheetsCounterTests(unittest.TestCase):
    def setUp(self):
        self.http = FakeSheets()
        self.now = 100
        self.counter = GoogleSheetsCounter("sheet-id", "Usage", http=self.http, clock=lambda: self.now)
        self.first = "a" * 32
        self.second = "b" * 32

    def test_reads_zero_without_writing_and_reuses_cache(self):
        self.assertEqual(self.counter.get_usage_count(), 0)
        self.assertEqual(self.counter.get_usage_count(), 0)
        self.assertEqual([call[0] for call in self.http.calls], ["GET"])

    def test_login_appends_once_and_a_new_server_reads_existing_count(self):
        self.assertEqual(self.counter.get_usage_count(self.first), 1)
        self.assertEqual(self.counter.get_usage_count(self.first), 1)
        restarted = GoogleSheetsCounter("sheet-id", "Usage", http=self.http)
        self.assertEqual(restarted.get_usage_count(self.first), 1)
        self.assertEqual(restarted.get_usage_count(self.second), 2)
        writes = [call for call in self.http.calls if call[0] == "POST"]
        self.assertEqual(len(writes), 2)
        self.assertEqual(writes[0][2]["params"]["valueInputOption"], "RAW")
        self.assertEqual(writes[0][2]["params"]["insertDataOption"], "INSERT_ROWS")

    def test_ambiguous_timeout_recovers_without_a_second_write(self):
        self.http.fail_after_append = True
        with self.assertRaises(SheetsCounterError):
            self.counter.get_usage_count(self.first)
        self.assertEqual(self.counter.get_usage_count(self.first), 1)
        self.assertEqual(len([call for call in self.http.calls if call[0] == "POST"]), 1)

    def test_duplicate_rows_do_not_inflate_total(self):
        self.http.rows += [[self.first], [self.first], [], [self.second]]
        self.assertEqual(self.counter.get_usage_count(), 2)

    def test_concurrent_logins_and_reruns(self):
        ids = [f"{i:032x}" for i in range(20)] * 2
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(self.counter.get_usage_count, ids))
        self.assertEqual(self.counter.get_usage_count(), 20)
        self.assertEqual(len(self.http.rows), 21)

    def test_cache_refreshes_external_changes(self):
        self.counter.get_usage_count()
        self.http.rows.append([self.first])
        self.now += 31
        self.assertEqual(self.counter.get_usage_count(), 1)

    def test_unrelated_sheet_is_not_overwritten(self):
        self.http.rows = [["customer_name"]]
        with self.assertRaises(SheetsCounterError):
            self.counter.get_usage_count(self.first)
        self.assertEqual([call[0] for call in self.http.calls], ["GET"])

    def test_http_errors_are_sanitized_and_do_not_report_zero(self):
        for status in (403, 404, 429, 500):
            with self.subTest(status=status):
                self.http.status = status
                with self.assertRaisesRegex(SheetsCounterError, f"HTTP {status}"):
                    self.counter.get_usage_count()

    def test_rejects_corrupt_rows_and_invalid_session_ids(self):
        for row in ([[123]], [["invalid"]], [[self.first, "extra"]]):
            with self.subTest(row=row):
                self.http.rows = [["session_id"]] + row
                with self.assertRaises(SheetsCounterError):
                    self.counter.get_usage_count()
        with self.assertRaises(ValueError):
            self.counter.get_usage_count("not-a-session")

    def test_sheet_name_is_quoted_and_url_encoded(self):
        counter = GoogleSheetsCounter("sheet-id", "Member's usage", http=self.http)
        counter.get_usage_count()
        self.assertIn("%27Member%27%27s%20usage%27%21A%3AB", self.http.calls[0][1])

    def test_daily_count_rolls_over_even_with_cached_sessions(self):
        before = datetime(2026, 11, 7, 15, 59, tzinfo=timezone.utc)
        after = datetime(2026, 11, 7, 16, 0, tzinfo=timezone.utc)
        self.assertEqual(self.counter.get_usage_stats(self.first, now=before), {"total": 1, "today": 1})
        self.assertEqual(self.counter.get_usage_stats(self.first, now=after), {"total": 1, "today": 0})
        self.assertEqual(self.counter.get_usage_stats(self.second, now=after), {"total": 2, "today": 1})

    def test_old_sheet_adds_timestamp_header_and_preserves_undated_rows(self):
        self.http.rows = [["session_id"], [self.first]]
        self.assertEqual(self.counter.get_usage_stats(self.first), {"total": 1, "today": 0})
        self.assertEqual(self.counter.get_usage_stats(self.second), {"total": 2, "today": 1})
        self.assertEqual(self.http.rows[0], ["session_id", "started_at_utc"])
        self.assertEqual(self.http.rows[1], [self.first])

    def test_duplicate_earliest_timestamp_determines_daily_count(self):
        self.http.rows += [[self.first, "2026-11-07T15:59:00+00:00"],
                           [self.first, "2026-11-07T16:01:00+00:00"],
                           [self.second, "2026-11-07T16:01:00+00:00"]]
        now = datetime(2026, 11, 7, 16, 5, tzinfo=timezone.utc)
        self.assertEqual(self.counter.get_usage_stats(now=now), {"total": 2, "today": 1})

    def test_unrelated_second_column_is_never_overwritten(self):
        self.http.rows = [["session_id", "customer_name"]]
        with self.assertRaises(SheetsCounterError):
            self.counter.get_usage_stats(self.first)
        self.assertEqual([call[0] for call in self.http.calls], ["GET"])


if __name__ == "__main__":
    unittest.main()
