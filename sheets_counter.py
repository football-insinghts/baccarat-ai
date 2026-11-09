"""Durable session counts using a dedicated Google Sheets tab."""

import re
import threading
import time
from datetime import datetime
from urllib.parse import quote

import requests
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials
from usage_counter import DEFAULT_TIMEZONE, day_bounds, utc_timestamp

SESSION_ID = re.compile(r"^[0-9a-f]{32}$")
SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"


class SheetsCounterError(RuntimeError):
    """An actionable error safe to log without exposing credentials or rows."""


class GoogleSheetsCounter:
    def __init__(self, spreadsheet_id, worksheet, credentials=None, *, http=None,
                 cache_seconds=30, clock=time.monotonic):
        self._clock = clock
        self._cache_seconds = cache_seconds
        self._expires = 0
        self._sessions = None
        self._has_timestamp_header = False
        self._lock = threading.Lock()
        sheet = "'" + worksheet.replace("'", "''") + "'"
        base_url = (
            "https://sheets.googleapis.com/v4/spreadsheets/"
            + quote(spreadsheet_id, safe="")
            + "/values/"
        )
        self._url = base_url + quote(sheet + "!A:B", safe="")
        self._header_url = base_url + quote(sheet + "!B1", safe="")
        try:
            if http is None:
                auth = Credentials.from_service_account_info(
                    credentials, scopes=[SHEETS_SCOPE]
                )
                http = AuthorizedSession(auth, refresh_timeout=10, max_refresh_attempts=1)
            self._http = http
        except (ValueError, GoogleAuthError):
            raise SheetsCounterError("Invalid Google Sheets service account configuration") from None

    def _request(self, method, url, **kwargs):
        try:
            response = self._http.request(method, url, timeout=10, **kwargs)
            if not 200 <= response.status_code < 300:
                raise SheetsCounterError(f"Google Sheets HTTP {response.status_code}")
            data = response.json()
            if not isinstance(data, dict):
                raise SheetsCounterError("Invalid Google Sheets response")
            return data
        except (requests.RequestException, GoogleAuthError, ValueError):
            raise SheetsCounterError("Google Sheets request failed; retry on the next app run") from None

    def _read_sessions(self):
        data = self._request("GET", self._url, params={"valueRenderOption": "UNFORMATTED_VALUE"})
        rows = data.get("values", [])
        # Never append to an unverified tab or treat unrelated data as usage.
        if not isinstance(rows, list) or not rows or rows[0] not in (
            ["session_id"], ["session_id", ""], ["session_id", "started_at_utc"]
        ):
            raise SheetsCounterError("Usage sheet must have session_id in A1 and started_at_utc or blank in B1")
        self._has_timestamp_header = rows[0] == ["session_id", "started_at_utc"]
        sessions = {}
        for row in rows[1:]:
            if not row or row == [""]:
                continue
            if (not isinstance(row, list) or len(row) > 2
                    or not isinstance(row[0], str) or not SESSION_ID.fullmatch(row[0])):
                raise SheetsCounterError("Usage sheet contains an invalid session ID")
            timestamp = None
            if len(row) == 2 and row[1] != "":
                try:
                    timestamp = utc_timestamp(datetime.fromisoformat(row[1]))
                except (ValueError, TypeError):
                    raise SheetsCounterError("Usage sheet contains an invalid timestamp") from None
            if row[0] not in sessions:
                sessions[row[0]] = timestamp
            elif sessions[row[0]] is None or timestamp is None:
                sessions[row[0]] = None
            else:
                sessions[row[0]] = min(sessions[row[0]], timestamp)
        self._sessions = sessions
        self._expires = self._clock() + self._cache_seconds

    def get_usage_count(self, session_id=None):
        return self.get_usage_stats(session_id)["total"]

    def get_usage_stats(self, session_id=None, *, started_at=None, now=None,
                        timezone_name=DEFAULT_TIMEZONE):
        if session_id is not None and (
            not isinstance(session_id, str) or not SESSION_ID.fullmatch(session_id)
        ):
            raise ValueError("Expected a random 32-character session ID")
        start, end = day_bounds(now, timezone_name)
        timestamp = utc_timestamp(started_at or now)
        with self._lock:
            try:
                fresh = False
                if self._sessions is None or self._clock() >= self._expires:
                    self._read_sessions()
                    fresh = True
                if session_id is not None and session_id not in self._sessions:
                    # Check the latest sheet before retrying a write or using a new
                    # server process. An earlier timed-out request may have committed.
                    if not fresh:
                        self._read_sessions()
                    if session_id not in self._sessions:
                        if not self._has_timestamp_header:
                            self._request("PUT", self._header_url,
                                          params={"valueInputOption": "RAW"},
                                          json={"values": [["started_at_utc"]]})
                            self._has_timestamp_header = True
                        data = self._request(
                            "POST", self._url + ":append",
                            params={"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"},
                            json={"values": [[session_id, timestamp.isoformat()]]},
                        )
                        updates = data.get("updates", {})
                        if not isinstance(updates, dict) or updates.get("updatedRows") != 1:
                            raise SheetsCounterError("Google Sheets did not confirm the appended session")
                        self._sessions[session_id] = timestamp
                # Unique IDs keep the total correct even if separate app instances
                # append the same ID concurrently. Never update a shared total cell.
                return {"total": len(self._sessions), "today": sum(
                    1 for value in self._sessions.values() if value is not None and start <= value < end
                )}
            except SheetsCounterError:
                self._sessions = None
                self._expires = 0
                raise
