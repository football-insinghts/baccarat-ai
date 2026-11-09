"""Validate deployment settings without storing credentials in source code."""

import re
from collections.abc import Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from usage_counter import DEFAULT_TIMEZONE

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


def load_usage_settings(secrets):
    """Counter configuration is separate so an outage does not prevent login."""
    storage = secrets.get("USAGE_STORAGE", "sqlite")
    timezone_name = secrets.get("USAGE_TIMEZONE", DEFAULT_TIMEZONE)
    try:
        ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, TypeError, ValueError):
        raise ValueError("USAGE_TIMEZONE must be a valid timezone name") from None
    if storage == "sqlite":
        return {"storage": storage, "timezone": timezone_name}
    if storage != "google_sheets":
        raise ValueError("USAGE_STORAGE must be sqlite or google_sheets")
    sheet_id = secrets.get("USAGE_SHEET_ID", "")
    worksheet = secrets.get("USAGE_SHEET_TAB", "Usage")
    if (not isinstance(sheet_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", sheet_id)
            or sheet_id.startswith("REPLACE_WITH_")):
        raise ValueError("Set USAGE_SHEET_ID to the spreadsheet ID")
    if not isinstance(worksheet, str) or not worksheet.strip():
        raise ValueError("Set USAGE_SHEET_TAB to the usage worksheet name")
    info = secrets.get("gcp_service_account")
    if not isinstance(info, Mapping):
        raise ValueError("Missing gcp_service_account settings")
    for name in ("client_email", "private_key"):
        value = info.get(name)
        if not isinstance(value, str) or not value.strip() or value.startswith("REPLACE_WITH_"):
            raise ValueError(f"Missing or invalid gcp_service_account.{name}")
    credentials = {
        "type": "service_account",
        "client_email": info["client_email"],
        "private_key": info["private_key"].replace("\\n", "\n"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    return {"storage": storage, "timezone": timezone_name, "spreadsheet_id": sheet_id,
            "worksheet": worksheet, "credentials": credentials}
