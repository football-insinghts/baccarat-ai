import unittest

from app_settings import REQUIRED_SETTINGS, load_settings, load_usage_settings


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.valid = {
            "GOOGLE_API_KEY": "test-key-not-a-real-credential",
            "APP_PASSWORD": "test-password",
            "GEMINI_MODEL": "test-model",
        }

    def test_accepts_valid_settings(self):
        self.assertEqual(load_settings(self.valid), self.valid)

    def test_missing_settings_fail_closed(self):
        for name in REQUIRED_SETTINGS:
            with self.subTest(name=name):
                values = self.valid.copy()
                del values[name]
                with self.assertRaises(ValueError):
                    load_settings(values)

    def test_blank_non_string_and_example_values_are_rejected(self):
        for name in REQUIRED_SETTINGS:
            for value in ("", "  ", None, 123, "REPLACE_WITH_EXAMPLE"):
                with self.subTest(name=name, value=value):
                    values = {**self.valid, name: value}
                    with self.assertRaises(ValueError) as error:
                        load_settings(values)
                    self.assertNotIn("test-password", str(error.exception))
                    self.assertNotIn("test-key-not-a-real-credential", str(error.exception))

    def test_preserves_password_whitespace(self):
        settings = load_settings({**self.valid, "APP_PASSWORD": " pass ", "GEMINI_MODEL": " test-model "})
        self.assertEqual(settings["APP_PASSWORD"], " pass ")
        self.assertEqual(settings["GEMINI_MODEL"], "test-model")

    def test_counter_defaults_to_sqlite(self):
        self.assertEqual(load_usage_settings(self.valid), {"storage": "sqlite", "timezone": "Asia/Shanghai"})

    def test_daily_counter_timezone_is_validated(self):
        self.assertEqual(load_usage_settings({"USAGE_TIMEZONE": "Asia/Bangkok"})["timezone"], "Asia/Bangkok")
        with self.assertRaises(ValueError):
            load_usage_settings({"USAGE_TIMEZONE": "invalid/timezone"})

    def test_google_sheets_configuration(self):
        settings = load_usage_settings({
            "USAGE_STORAGE": "google_sheets",
            "USAGE_SHEET_ID": "sheet-id",
            "gcp_service_account": {"client_email": "test@example.invalid", "private_key": "line1\\nline2"},
        })
        self.assertEqual(settings["worksheet"], "Usage")
        self.assertEqual(settings["credentials"]["private_key"], "line1\nline2")
        self.assertEqual(settings["credentials"]["token_uri"], "https://oauth2.googleapis.com/token")

    def test_incomplete_google_config_never_falls_back_to_local(self):
        for invalid in (
            {"USAGE_STORAGE": "unknown"},
            {"USAGE_STORAGE": "google_sheets"},
            {"USAGE_STORAGE": "google_sheets", "USAGE_SHEET_ID": "sheet-id"},
            {"USAGE_STORAGE": "google_sheets", "USAGE_SHEET_ID": "https://docs.google.com/test"},
        ):
            with self.subTest(settings=invalid), self.assertRaises(ValueError):
                load_usage_settings(invalid)


if __name__ == "__main__":
    unittest.main()
