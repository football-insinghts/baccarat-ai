"""Validate deployment settings without storing credentials in source code."""

REQUIRED_SETTINGS = ("GOOGLE_API_KEY", "APP_PASSWORD", "GEMINI_MODEL")


def load_settings(secrets):
    settings = {}
    for name in REQUIRED_SETTINGS:
        value = secrets.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Missing or invalid secret: {name}")
        if value.startswith("REPLACE_WITH_"):
            raise ValueError(f"Replace the example secret: {name}")
        settings[name] = value if name == "APP_PASSWORD" else value.strip()
    return settings
