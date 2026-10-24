import unittest

from app_settings import REQUIRED_SETTINGS, load_settings


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


if __name__ == "__main__":
    unittest.main()
