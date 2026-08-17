import sqlite3
from contextlib import contextmanager

import xbmcvfs

from .migrations import MIGRATIONS

_DB_FILENAME = "lists.db"


class DatabaseManager(object):
    """Owns the SQLite connection for this addon's own database.

    Never touches vStream's database, settings, history or bookmarks.
    """

    def __init__(self, profile_path):
        real_path = xbmcvfs.translatePath(profile_path)
        if not xbmcvfs.exists(real_path):
            xbmcvfs.mkdirs(real_path)
        self._db_path = real_path.rstrip("/\\") + "/" + _DB_FILENAME
        self._migrate()

    def _connect(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _migrate(self):
        conn = self._connect()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)"
            )
            row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
            current = row["v"] if row and row["v"] is not None else 0

            for index, script in enumerate(MIGRATIONS, start=1):
                if index <= current:
                    continue
                conn.executescript(script)
                conn.execute("INSERT INTO schema_version (version) VALUES (?)", (index,))
            conn.commit()
        finally:
            conn.close()

    @contextmanager
    def connection(self):
        """Auto-committing connection for simple reads/writes."""
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    @contextmanager
    def transaction(self):
        """Explicit BEGIN/COMMIT/ROLLBACK for multi-step operations
        (e.g. moving an item between lists) so a failure can't leave
        the database half-updated.
        """
        conn = self._connect()
        try:
            conn.execute("BEGIN")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
