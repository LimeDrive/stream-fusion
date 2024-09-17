"""Interaction with SQLite database."""
# TODO: Breaking this with postgress and redis, and add method for key management
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY

from stream_fusion.logging_config import logger
from stream_fusion.settings import settings


class SQLiteAccess:
    """Class handling SQLite connection and operations."""

    def __init__(self):
        self.db_location = settings.db_path
        self.expiration_limit = getattr(settings, "security_api_key_expiration", 15)
        if self.expiration_limit == 15:
            logger.warning(
                "Security API key expiration not found or invalid in settings. Using default value of 15 days."
            )
        self.init_db()

    def init_db(self):
        """Initialize the database and perform necessary migrations."""
        with sqlite3.connect(self.db_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stream_fusion_security (
                    api_key TEXT PRIMARY KEY,
                    is_active INTEGER,
                    never_expire INTEGER,
                    expiration_date TEXT,
                    latest_query_date TEXT,
                    total_queries INTEGER,
                    name TEXT
                )
            """
            )
            conn.commit()

    def create_key(self, name: str, never_expire: bool) -> str:
        """Create a new API key."""
        api_key = str(uuid.uuid4())
        expiration_date = (
            (datetime.utcnow() + timedelta(days=self.expiration_limit)).isoformat(
                timespec="seconds"
            )
            if not never_expire
            else None
        )

        with sqlite3.connect(self.db_location) as conn:
            conn.execute(
                """
                INSERT INTO stream_fusion_security (
                    api_key,
                    is_active,
                    never_expire,
                    expiration_date,
                    latest_query_date,
                    total_queries, name) VALUES (?, 1, ?, ?, NULL, 0, ?)
            """,
                (api_key, int(never_expire), expiration_date, name),
            )
        return api_key

    def renew_key(self, api_key: str, new_expiration_date: Optional[str] = None) -> str:
        """Renew an existing API key."""
        with sqlite3.connect(self.db_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT is_active, never_expire FROM stream_fusion_security WHERE api_key = ?",
                (api_key,),
            )
            result = cursor.fetchone()

            if not result:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND, detail="API key not found"
                )

            is_active, never_expire = result
            response_lines = []

            if not is_active:
                response_lines.append(
                    "This API key was revoked and has been reactivated."
                )

            if not never_expire:
                if not new_expiration_date:
                    new_expiration_date = (
                        datetime.utcnow() + timedelta(days=self.expiration_limit)
                    ).isoformat(timespec="seconds")
                else:
                    try:
                        new_expiration_date = datetime.fromisoformat(
                            new_expiration_date
                        ).isoformat(timespec="seconds")
                    except ValueError:
                        raise HTTPException(
                            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="The expiration date could not be parsed. Please use ISO 8601 format.",
                        )

                cursor.execute(
                    "UPDATE stream_fusion_security SET expiration_date = ?, is_active = 1 WHERE api_key = ?",
                    (new_expiration_date, api_key),
                )
                response_lines.append(
                    f"The new expiration date for the API key is {new_expiration_date}"
                )

            return " ".join(response_lines)

    def revoke_key(self, api_key: str):
        """Revoke an API key."""
        with sqlite3.connect(self.db_location) as conn:
            conn.execute(
                "UPDATE stream_fusion_security SET is_active = 0 WHERE api_key = ?",
                (api_key,),
            )

    def check_key(self, api_key: str) -> bool:
        """Check if an API key is valid."""
        with sqlite3.connect(self.db_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT is_active, total_queries, expiration_date, never_expire FROM stream_fusion_security WHERE api_key = ?",
                (api_key,),
            )
            result = cursor.fetchone()

            if (
                not result
                or not result[0]
                or (
                    not result[3]
                    and datetime.fromisoformat(result[2]) < datetime.utcnow()
                )
            ):
                return False

            threading.Thread(
                target=self._update_usage, args=(api_key, result[1])
            ).start()
            return True

    def _update_usage(self, api_key: str, usage_count: int):
        """Update usage statistics for an API key."""
        with sqlite3.connect(self.db_location) as conn:
            conn.execute(
                "UPDATE stream_fusion_security SET total_queries = ?, latest_query_date = ? WHERE api_key = ?",
                (
                    usage_count + 1,
                    datetime.utcnow().isoformat(timespec="seconds"),
                    api_key,
                ),
            )

    def get_usage_stats(self) -> List[Tuple[str, bool, bool, str, str, int, str]]:
        """Return usage statistics for all API keys."""
        with sqlite3.connect(self.db_location) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT api_key, is_active, never_expire, expiration_date, latest_query_date, total_queries, name
                FROM stream_fusion_security
                ORDER BY latest_query_date DESC
            """
            )
            return cursor.fetchall()


security_db_access = SQLiteAccess()
