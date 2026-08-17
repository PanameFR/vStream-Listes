# Schema migrations for lists.db. Each entry is applied once, in order,
# and recorded in schema_version so addon updates never touch existing data.

MIGRATIONS = [
    # 1: initial schema
    """
    CREATE TABLE IF NOT EXISTS lists (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        position    INTEGER NOT NULL DEFAULT 0,
        created_at  TEXT NOT NULL,
        updated_at  TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS media (
        media_type          TEXT NOT NULL,
        tmdb_id             INTEGER NOT NULL,
        title               TEXT,
        original_title      TEXT,
        year                TEXT,
        overview            TEXT,
        poster_path         TEXT,
        backdrop_path       TEXT,
        genres              TEXT,
        runtime             INTEGER,
        rating              REAL,
        metadata_updated_at TEXT,
        PRIMARY KEY (media_type, tmdb_id)
    );

    CREATE TABLE IF NOT EXISTS list_items (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        list_id     INTEGER NOT NULL REFERENCES lists(id) ON DELETE CASCADE,
        media_type  TEXT NOT NULL,
        tmdb_id     INTEGER NOT NULL,
        position    INTEGER NOT NULL DEFAULT 0,
        added_at    TEXT NOT NULL,
        UNIQUE(list_id, media_type, tmdb_id)
    );

    CREATE INDEX IF NOT EXISTS idx_list_items_list ON list_items(list_id);
    CREATE INDEX IF NOT EXISTS idx_list_items_media ON list_items(media_type, tmdb_id);
    """,
]
