import time
import sqlite3
import asyncio
from typing import Optional
from pathlib import Path

class Database:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.db_path = Path(db_path)
        
    async def connect(self) -> None:
        """Создаем базу данных и таблицы"""
        # Создаем директорию если нужно
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Создаем таблицы
        await self.migrate()
        
    async def close(self) -> None:
        """Закрываем соединение"""
        pass  # SQLite не требует явного закрытия
        
    async def migrate(self) -> None:
        """Создаем таблицы"""
        def _create_tables():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Таблица пользователей
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_at INTEGER
                )
            """)
            
            # Таблица событий
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    source TEXT,
                    created_at INTEGER
                )
            """)
            
            # Индекс для событий
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_user_type 
                ON events(user_id, type)
            """)
            
            # Таблица приглашений
            cur.execute("""
                CREATE TABLE IF NOT EXISTS invites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    link TEXT,
                    expire_at INTEGER,
                    created_at INTEGER
                )
            """)
            
            # Таблица ключ-значение
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kv (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            # Таблица заявок
            cur.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    tg_username TEXT NOT NULL,
                    source TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at INTEGER NOT NULL
                )
            """)
            
            # Индекс для заявок
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_submissions_user_created 
                ON submissions(user_id, created_at DESC)
            """)
            
            conn.commit()
            conn.close()
            
        # Запускаем в thread pool для избежания блокировки
        await asyncio.get_event_loop().run_in_executor(None, _create_tables)

    async def upsert_user(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> None:
        """Добавляем или обновляем пользователя"""
        def _upsert():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            now = int(time.time())
            
            cur.execute("""
                INSERT OR REPLACE INTO users(user_id, username, first_name, joined_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, now))
            
            conn.commit()
            conn.close()
            
        await asyncio.get_event_loop().run_in_executor(None, _upsert)

    async def add_event(self, user_id: int, event_type: str, source: Optional[str]) -> None:
        """Добавляем событие"""
        def _add_event():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            now = int(time.time())
            
            cur.execute("""
                INSERT INTO events(user_id, type, source, created_at) 
                VALUES (?, ?, ?, ?)
            """, (user_id, event_type, source, now))
            
            conn.commit()
            conn.close()
            
        await asyncio.get_event_loop().run_in_executor(None, _add_event)

    async def get_last_event_time(self, user_id: int, event_type: str) -> Optional[int]:
        """Получаем время последнего события"""
        def _get_time():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT created_at FROM events 
                WHERE user_id=? AND type=? 
                ORDER BY created_at DESC LIMIT 1
            """, (user_id, event_type))
            
            row = cur.fetchone()
            conn.close()
            return row[0] if row else None
            
        return await asyncio.get_event_loop().run_in_executor(None, _get_time)

    async def user_has_event_after(self, user_id: int, event_type: str, after_ts: int | None) -> bool:
        """Проверяем есть ли событие после указанного времени"""
        def _check():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            if after_ts is None:
                cur.execute("""
                    SELECT 1 FROM events 
                    WHERE user_id=? AND type=? LIMIT 1
                """, (user_id, event_type))
            else:
                cur.execute("""
                    SELECT 1 FROM events 
                    WHERE user_id=? AND type=? AND created_at > ? LIMIT 1
                """, (user_id, event_type, after_ts))
                
            row = cur.fetchone()
            conn.close()
            return row is not None
            
        return await asyncio.get_event_loop().run_in_executor(None, _check)

    async def set_user_source(self, user_id: int, source: str) -> None:
        """Устанавливаем источник пользователя"""
        def _set_source():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT OR REPLACE INTO kv(key, value) 
                VALUES (?, ?)
            """, (f"user_source_{user_id}", source))
            
            conn.commit()
            conn.close()
            
        await asyncio.get_event_loop().run_in_executor(None, _set_source)

    async def get_user_source(self, user_id: int) -> Optional[str]:
        """Получаем источник пользователя"""
        def _get_source():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute("SELECT value FROM kv WHERE key=?", (f"user_source_{user_id}",))
            row = cur.fetchone()
            conn.close()
            return row[0] if row else None
            
        return await asyncio.get_event_loop().run_in_executor(None, _get_source)

    async def get_kv(self, key: str) -> Optional[str]:
        """Получаем значение по ключу"""
        def _get():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute("SELECT value FROM kv WHERE key=?", (key,))
            row = cur.fetchone()
            conn.close()
            return row[0] if row else None
            
        return await asyncio.get_event_loop().run_in_executor(None, _get)

    async def set_kv(self, key: str, value: str) -> None:
        """Устанавливаем значение по ключу"""
        def _set():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT OR REPLACE INTO kv(key, value) 
                VALUES (?, ?)
            """, (key, value))
            
            conn.commit()
            conn.close()
            
        await asyncio.get_event_loop().run_in_executor(None, _set)

    async def save_invite(self, user_id: int, link: str, expire_at: int) -> None:
        """Сохраняем приглашение"""
        def _save():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            now = int(time.time())
            
            cur.execute("""
                INSERT INTO invites(user_id, link, expire_at, created_at) 
                VALUES (?, ?, ?, ?)
            """, (user_id, link, expire_at, now))
            
            conn.commit()
            conn.close()
            
        await asyncio.get_event_loop().run_in_executor(None, _save)

    async def insert_submission(self, user_id: int, email: str, tg_username: str, source: Optional[str]) -> int:
        """Добавляем новую заявку"""
        def _insert():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            now = int(time.time())
            
            cur.execute("""
                INSERT INTO submissions(user_id, email, tg_username, source, status, created_at) 
                VALUES (?, ?, ?, ?, 'pending', ?)
            """, (user_id, email, tg_username, source, now))
            
            submission_id = cur.lastrowid
            conn.commit()
            conn.close()
            return submission_id
            
        return await asyncio.get_event_loop().run_in_executor(None, _insert)

    async def update_submission_status(self, submission_id: int, status: str) -> None:
        """Обновляем статус заявки"""
        def _update():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE submissions SET status = ? WHERE id = ?
            """, (status, submission_id))
            
            conn.commit()
            conn.close()
            
        await asyncio.get_event_loop().run_in_executor(None, _update)

    async def get_latest_pending_submission_by_user(self, user_id: int):
        """Получаем последнюю pending заявку пользователя"""
        def _get():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT * FROM submissions 
                WHERE user_id = ? AND status = 'pending' 
                ORDER BY created_at DESC LIMIT 1
            """, (user_id,))
            
            # Get column names
            columns = [description[0] for description in cur.description]
            row = cur.fetchone()
            conn.close()
            if row:
                # Convert tuple to dict-like object
                return dict(zip(columns, row))
            return None
            
        return await asyncio.get_event_loop().run_in_executor(None, _get)

    async def get_submission_by_id(self, submission_id: int):
        """Получаем заявку по ID"""
        def _get():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT * FROM submissions WHERE id = ?
            """, (submission_id,))
            
            # Get column names
            columns = [description[0] for description in cur.description]
            row = cur.fetchone()
            conn.close()
            if row:
                # Convert tuple to dict-like object
                return dict(zip(columns, row))
            return None
            
        return await asyncio.get_event_loop().run_in_executor(None, _get)
