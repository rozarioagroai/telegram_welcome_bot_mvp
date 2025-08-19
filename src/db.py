import time
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from .config import settings

class Database:
    def __init__(self, _unused_path: str | None = None):
        if not settings.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is required for Postgres backend")
        # SSL обязателен на Neon: ?sslmode=require в URL
        self.pool = AsyncConnectionPool(settings.DATABASE_URL, kwargs={"row_factory": dict_row}, min_size=1, max_size=5)

    async def connect(self) -> None:
        await self.pool.open()

    async def close(self) -> None:
        await self.pool.close()

    async def migrate(self) -> None:
        async with self.pool.connection() as aconn:
            async with aconn.cursor() as cur:
                await cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_at BIGINT
                );
                CREATE TABLE IF NOT EXISTS events (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT,
                    type TEXT,
                    source TEXT,
                    created_at BIGINT
                );
                CREATE INDEX IF NOT EXISTS idx_events_user_type ON events(user_id, type);

                CREATE TABLE IF NOT EXISTS invites (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT,
                    link TEXT,
                    expire_at BIGINT,
                    created_at BIGINT
                );

                CREATE TABLE IF NOT EXISTS kv (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );

                CREATE TABLE IF NOT EXISTS submissions (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    email TEXT NOT NULL,
                    tg_username TEXT NOT NULL,
                    source TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at BIGINT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_submissions_user_created ON submissions(user_id, created_at DESC);
                """)
                await aconn.commit()

    async def upsert_user(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> None:
        now = int(time.time())
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO users(user_id, username, first_name, joined_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET username=EXCLUDED.username, first_name=EXCLUDED.first_name
                """,
                (user_id, username, first_name, now),
            )
            await aconn.commit()

    async def add_event(self, user_id: int, event_type: str, source: Optional[str]) -> None:
        now = int(time.time())
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            await cur.execute(
                "INSERT INTO events(user_id, type, source, created_at) VALUES (%s, %s, %s, %s)",
                (user_id, event_type, source, now),
            )
            await aconn.commit()

    async def get_last_event_time(self, user_id: int, event_type: str) -> Optional[int]:
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            await cur.execute(
                "SELECT created_at FROM events WHERE user_id=%s AND type=%s ORDER BY created_at DESC LIMIT 1",
                (user_id, event_type),
            )
            row = await cur.fetchone()
            return int(row["created_at"]) if row else None

    async def user_has_event_after(self, user_id: int, event_type: str, after_ts: int | None) -> bool:
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            if after_ts is None:
                await cur.execute("SELECT 1 FROM events WHERE user_id=%s AND type=%s LIMIT 1", (user_id, event_type))
            else:
                await cur.execute(
                    "SELECT 1 FROM events WHERE user_id=%s AND type=%s AND created_at>=%s LIMIT 1",
                    (user_id, event_type, after_ts),
                )
            return (await cur.fetchone()) is not None

    async def has_valid_captcha(self, user_id: int) -> bool:
        last_start = await self.get_last_event_time(user_id, "start")
        return await self.user_has_event_after(user_id, "captcha_ok", last_start)

    async def set_kv(self, key: str, value: str) -> None:
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO kv(key, value) VALUES(%s, %s)
                ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value
                """,
                (key, value),
            )
            await aconn.commit()

    async def get_kv(self, key: str) -> Optional[str]:
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            await cur.execute("SELECT value FROM kv WHERE key=%s", (key,))
            row = await cur.fetchone()
            return row["value"] if row else None

    async def save_invite(self, user_id: int, link: str, expire_at: int) -> None:
        now = int(time.time())
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            await cur.execute(
                "INSERT INTO invites(user_id, link, expire_at, created_at) VALUES(%s, %s, %s, %s)",
                (user_id, link, expire_at, now),
            )
            await aconn.commit()

    async def set_user_source(self, user_id: int, source: str) -> None:
        await self.set_kv(f"user:{user_id}:source", source)

    async def get_user_source(self, user_id: int) -> Optional[str]:
        return await self.get_kv(f"user:{user_id}:source")

    async def insert_submission(self, user_id: int, email: str, tg_username: str, source: Optional[str]) -> int:
        now = int(time.time())
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            await cur.execute(
                "INSERT INTO submissions(user_id, email, tg_username, source, status, created_at) VALUES(%s,%s,%s,%s,'pending',%s) RETURNING id",
                (user_id, email, tg_username, source, now),
            )
            row = await cur.fetchone()
            await aconn.commit()
            return int(row["id"])

    async def update_submission_status(self, submission_id: int, status: str) -> None:
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            await cur.execute("UPDATE submissions SET status=%s WHERE id=%s", (status, submission_id))
            await aconn.commit()

    async def get_latest_pending_submission_by_user(self, user_id: int):
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM submissions WHERE user_id=%s AND status='pending' ORDER BY created_at DESC LIMIT 1",
                (user_id,),
            )
            return await cur.fetchone()

    async def get_submission_by_id(self, submission_id: int):
        async with self.pool.connection() as aconn, aconn.cursor() as cur:
            await cur.execute("SELECT * FROM submissions WHERE id=%s", (submission_id,))
            return await cur.fetchone()