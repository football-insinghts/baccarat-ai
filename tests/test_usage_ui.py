import re
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest

from usage_counter import get_usage_count
from sheets_counter import SheetsCounterError


ROOT = Path(__file__).resolve().parents[1]


class UsageUITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "usage.sqlite3"
        database_patch = patch("usage_counter.DEFAULT_DATABASE_PATH", self.database)
        database_patch.start()
        self.addCleanup(database_patch.stop)

    def app(self):
        app = AppTest.from_file(str(ROOT / "Baccarat_ai.py"), default_timeout=15)
        app.secrets.update({
            "GOOGLE_API_KEY": "unused-test-key",
            "APP_PASSWORD": "counter-test-password",
            "GEMINI_MODEL": "unused-test-model",
        })
        app.run()
        self.assertFalse(app.exception)
        return app

    def displayed_count(self, app, kind="total"):
        for markdown in app.markdown:
            match = re.search(r'data-count="' + kind + r'">([\d,]+)</strong>', markdown.value)
            if match:
                return int(match[1].replace(",", ""))
        self.fail("Counter was not rendered")

    def login(self, app, password="counter-test-password"):
        app.text_input[0].set_value(password)
        app.button[0].click().run()
        self.assertFalse(app.exception)

    def test_login_page_and_wrong_password_hide_counter_and_do_not_increment(self):
        app = self.app()
        self.assertFalse(any('class="usage-counter"' in item.value for item in app.markdown))
        self.assertFalse(self.database.exists())
        self.login(app, "wrong-password")
        self.assertTrue(app.error)
        self.assertFalse(any('class="usage-counter"' in item.value for item in app.markdown))
        self.assertFalse(self.database.exists())
        self.assertEqual(get_usage_count(), 0)

    def test_successful_login_counts_once_across_reruns(self):
        app = self.app()
        self.login(app)
        self.assertEqual(self.displayed_count(app), 1)
        self.assertEqual(self.displayed_count(app, "today"), 1)
        self.assertEqual(len(app.get("file_uploader")), 1)
        self.assertTrue(app.button[0].disabled)
        markup = [item.value for item in app.markdown]
        result_index = next(i for i, value in enumerate(markup) if 'class="empty-result"' in value)
        counter_index = next(i for i, value in enumerate(markup) if 'class="usage-counter"' in value)
        footer_index = next(i for i, value in enumerate(markup) if 'class="app-footer"' in value)
        self.assertLess(result_index, counter_index)
        self.assertLess(counter_index, footer_index)
        app.run()
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(self.displayed_count(app), 1)
        self.assertEqual(get_usage_count(), 1)

    def test_separate_sessions_share_the_total(self):
        first = self.app()
        second = self.app()
        self.login(first)
        second.run()
        self.assertFalse(any('class="usage-counter"' in item.value for item in second.markdown))
        self.login(second)
        self.assertEqual(self.displayed_count(second), 2)
        first.run()
        self.assertEqual(self.displayed_count(first), 2)
        self.assertEqual(get_usage_count(), 2)

    def test_storage_failure_does_not_block_login_and_retry_is_counted_once(self):
        app = self.app()
        with patch("usage_counter.get_usage_stats", side_effect=sqlite3.OperationalError("locked")):
            self.login(app)
            self.assertEqual(len(app.get("file_uploader")), 1)
            self.assertTrue(any("ไม่พร้อมแสดงชั่วคราว" in item.value for item in app.caption))
        self.assertEqual(get_usage_count(), 0)
        app.run()
        self.assertEqual(self.displayed_count(app), 1)
        app.run()
        self.assertEqual(self.displayed_count(app), 1)

    def use_sheets(self, app):
        app.secrets.update({
            "USAGE_STORAGE": "google_sheets",
            "USAGE_SHEET_ID": self.database.parent.name.replace(".", "-"),
            "gcp_service_account": {"client_email": "fake@example.invalid", "private_key": "fake-test-key"},
        })

    def test_google_backend_is_used_for_login_and_never_writes_sqlite(self):
        app = self.app()
        self.use_sheets(app)
        sessions = set()

        def count(session_id, **kwargs):
            if session_id is not None:
                sessions.add(session_id)
            return {"total": len(sessions), "today": len(sessions)}

        counter = Mock()
        counter.get_usage_stats.side_effect = count
        with patch("sheets_counter.GoogleSheetsCounter", return_value=counter), patch("usage_counter.get_usage_stats") as local:
            app.run()
            self.assertFalse(any('class="usage-counter"' in item.value for item in app.markdown))
            counter.get_usage_stats.assert_not_called()
            self.login(app)
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(self.displayed_count(app), 1)
            local.assert_not_called()

    def test_google_failure_keeps_app_available_without_using_local_total(self):
        app = self.app()
        self.use_sheets(app)
        counter = Mock()
        counter.get_usage_stats.side_effect = SheetsCounterError("Google Sheets HTTP 403")
        with patch("sheets_counter.GoogleSheetsCounter", return_value=counter), patch("usage_counter.get_usage_stats") as local:
            self.login(app)
            self.assertEqual(len(app.get("file_uploader")), 1)
            self.assertTrue(any("ไม่พร้อมแสดงชั่วคราว" in item.value for item in app.caption))
            local.assert_not_called()


if __name__ == "__main__":
    unittest.main()
