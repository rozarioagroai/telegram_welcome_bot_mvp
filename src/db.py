import aiosqlite
import sqlite3
import time
from typing import Any, Optional

class Database:
    def __init__(self, path: str):
        self.path = path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        await self._conn.execute("PRAGMA journal_mode=WAL;")
        await self._conn.execute("PRAGMA foreign_keys=ON;")
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def migrate(self) -> None:
        assert self._conn
        await self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at INTEGER
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                source TEXT,
                created_at INTEGER
            );
            CREATE INDEX IF NOT EXISTS idx_events_user_type ON events(user_id, type);

            CREATE TABLE IF NOT EXISTS invites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                link TEXT,
                expire_at INTEGER,
                created_at INTEGER
            );

            CREATE TABLE IF NOT EXISTS kv (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            -- NEW: submissions from users (email + @username)
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                tg_username TEXT NOT NULL,
                source TEXT,
                status TEXT NOT NULL DEFAULT 'pending', -- pending|approved|denied
                created_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_submissions_user_created ON submissions(user_id, created_at DESC);
            """
        )
        await self._conn.commit()

    async def upsert_user(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> None:
        assert self._conn
        now = int(time.time())
        await self._conn.execute(
            """
            INSERT INTO users(user_id, username, first_name, joined_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, first_name=excluded.first_name
            """,
            (user_id, username, first_name, now),
        )
        await self._conn.commit()

    async def add_event(self, user_id: int, event_type: str, source: Optional[str]) -> None:
        assert self._conn
        now = int(time.time())
        await self._conn.execute(
            "INSERT INTO events(user_id, type, source, created_at) VALUES (?, ?, ?, ?)",
            (user_id, event_type, source, now),
        )
        await self._conn.commit()

    async def get_last_event_time(self, user_id: int, event_type: str) -> Optional[int]:
        assert self._conn
        async with self._conn.execute(
            "SELECT created_at FROM events WHERE user_id=? AND type=? ORDER BY created_at DESC LIMIT 1",
            (user_id, event_type),
        ) as cur:
            row = await cur.fetchone()
            return int(row["created_at"]) if row else None

    async def user_has_event_after(self, user_id: int, event_type: str, after_ts: int | None) -> bool:
        assert self._conn
        if after_ts is None:
            async with self._conn.execute(
                "SELECT 1 FROM events WHERE user_id=? AND type=? LIMIT 1", (user_id, event_type)
            ) as cur:
                return await cur.fetchone() is not None
        else:
            async with self._conn.execute(
                "SELECT 1 FROM events WHERE user_id=? AND type=? AND created_at>=? LIMIT 1",
                (user_id, event_type, after_ts),
            ) as cur:
                return await cur.fetchone() is not None

    async def has_valid_captcha(self, user_id: int) -> bool:
        last_start = await self.get_last_event_time(user_id, "start")
        return await self.user_has_event_after(user_id, "captcha_ok", last_start)

    async def set_kv(self, key: str, value: str) -> None:
        assert self._conn
        await self._conn.execute(
            """
            INSERT INTO kv(key, value) VALUES(?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key, value),
        )
        await self._conn.commit()

    async def get_kv(self, key: str) -> Optional[str]:
        assert self._conn
        async with self._conn.execute("SELECT value FROM kv WHERE key=?", (key,)) as cur:
            row = await cur.fetchone()
            return row["value"] if row else None

    async def save_invite(self, user_id: int, link: str, expire_at: int) -> None:
        assert self._conn
        now = int(time.time())
        await self._conn.execute(
            "INSERT INTO invites(user_id, link, expire_at, created_at) VALUES(?, ?, ?, ?)",
            (user_id, link, expire_at, now),
        )
        await self._conn.commit()

    async def set_user_source(self, user_id: int, source: str) -> None:
        await self.set_kv(f"user:{user_id}:source", source)

    async def get_user_source(self, user_id: int) -> Optional[str]:
        return await self.get_kv(f"user:{user_id}:source")

    # -------- submissions ----------
    async def insert_submission(self, user_id: int, email: str, tg_username: str, source: Optional[str]) -> int:
        assert self._conn
        now = int(time.time())
        cur = await self._conn.execute(
            "INSERT INTO submissions(user_id, email, tg_username, source, status, created_at) VALUES(?, ?, ?, ?, 'pending', ?)",
            (user_id, email, tg_username, source, now),
        )
        await self._conn.commit()
        return int(cur.lastrowid)

    async def update_submission_status(self, submission_id: int, status: str) -> None:
        assert self._conn
        await self._conn.execute(
            "UPDATE submissions SET status=? WHERE id=?",
            (status, submission_id),
        )
        await self._conn.commit()

    async def get_latest_pending_submission_by_user(self, user_id: int) -> Optional[sqlite3.Row]:
        assert self._conn
        async with self._conn.execute(
            "SELECT * FROM submissions WHERE user_id=? AND status='pending' ORDER BY created_at DESC LIMIT 1",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            return row

    async def get_submission_by_id(self, submission_id: int) -> Optional[sqlite3.Row]:
        assert self._conn
        async with self._conn.execute("SELECT * FROM submissions WHERE id=?", (submission_id,)) as cur:
            return await cur.fetchone()