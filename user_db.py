"""SQLite storage for favorites, play counts, and playlists (one profile name = one user)."""
import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "user_data.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS favorites (
    username TEXT NOT NULL, track_id TEXT NOT NULL,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, track_id)
);
CREATE TABLE IF NOT EXISTS plays (
    username TEXT NOT NULL, track_id TEXT NOT NULL,
    play_count INTEGER NOT NULL DEFAULT 0,
    last_played TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, track_id)
);
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL, name TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (username, name)
);
CREATE TABLE IF NOT EXISTS playlist_tracks (
    playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    track_id TEXT NOT NULL,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (playlist_id, track_id)
);
"""


def _conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with closing(_conn()) as c, c:
        c.executescript(SCHEMA)


# ---------- favorites ----------
def favorite_ids(user):
    with closing(_conn()) as c:
        rows = c.execute("SELECT track_id FROM favorites WHERE username=? ORDER BY added_at DESC", (user,))
        return [r["track_id"] for r in rows]


def toggle_favorite(user, track_id):
    with closing(_conn()) as c, c:
        gone = c.execute("DELETE FROM favorites WHERE username=? AND track_id=?", (user, track_id)).rowcount
        if not gone:
            c.execute("INSERT INTO favorites (username, track_id) VALUES (?, ?)", (user, track_id))


# ---------- plays ----------
def log_play(user, track_id):
    with closing(_conn()) as c, c:
        c.execute(
            """INSERT INTO plays (username, track_id, play_count) VALUES (?, ?, 1)
               ON CONFLICT(username, track_id)
               DO UPDATE SET play_count = play_count + 1, last_played = CURRENT_TIMESTAMP""",
            (user, track_id),
        )


def play_counts(user):
    with closing(_conn()) as c:
        rows = c.execute("SELECT track_id, play_count FROM plays WHERE username=?", (user,))
        return {r["track_id"]: r["play_count"] for r in rows}


def most_played_ids(user, limit=25):
    with closing(_conn()) as c:
        rows = c.execute(
            "SELECT track_id FROM plays WHERE username=? ORDER BY play_count DESC, last_played DESC LIMIT ?",
            (user, limit),
        )
        return [r["track_id"] for r in rows]


# ---------- playlists ----------
def create_playlist(user, name):
    """Returns the new playlist id, or None if the name is blank or already used."""
    name = name.strip()
    if not name:
        return None
    try:
        with closing(_conn()) as c, c:
            return c.execute("INSERT INTO playlists (username, name) VALUES (?, ?)", (user, name)).lastrowid
    except sqlite3.IntegrityError:
        return None


def list_playlists(user):
    with closing(_conn()) as c:
        rows = c.execute("SELECT id, name FROM playlists WHERE username=? ORDER BY created_at", (user,))
        return [(r["id"], r["name"]) for r in rows]


def delete_playlist(playlist_id):
    with closing(_conn()) as c, c:
        c.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))


def add_to_playlist(playlist_id, track_id):
    with closing(_conn()) as c, c:
        c.execute("INSERT OR IGNORE INTO playlist_tracks (playlist_id, track_id) VALUES (?, ?)",
                  (playlist_id, track_id))


def remove_from_playlist(playlist_id, track_id):
    with closing(_conn()) as c, c:
        c.execute("DELETE FROM playlist_tracks WHERE playlist_id=? AND track_id=?", (playlist_id, track_id))


def playlist_track_ids(playlist_id):
    with closing(_conn()) as c:
        rows = c.execute("SELECT track_id FROM playlist_tracks WHERE playlist_id=? ORDER BY added_at",
                         (playlist_id,))
        return [r["track_id"] for r in rows]