"""Модели базы данных SQLite для хранения контекста диалогов."""

from __future__ import annotations

from pathlib import Path

import aiosqlite
from beartype import beartype


@beartype
async def init_database(db_path: Path) -> None:
    """Инициализировать базу данных (создать таблицы).

    Args:
        db_path: Путь к файлу базы данных
    """
    # Создать папку storage если её нет
    db_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(db_path) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица сообщений (история диалогов)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,  -- 'user' или 'assistant'
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tokens_used INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Индексы для быстрого поиска
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_user_id 
            ON messages(user_id)
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
            ON messages(timestamp)
        """)

        # Таблица тикетов (для handoff)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ticket_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                summary TEXT NOT NULL,
                context_json TEXT NOT NULL,
                requested_action TEXT,
                sla_deadline_at DATETIME,
                status TEXT DEFAULT 'open',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Таблица событий (для метрик)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Таблица слотов (для отслеживания собранных параметров)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                slot_name TEXT NOT NULL,
                slot_value TEXT NOT NULL,
                extracted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Таблица согласий (для GDPR compliance)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_consents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                consent_type TEXT NOT NULL,
                granted INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Индексы для новых таблиц
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id)
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id)
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_slots_user_id ON slots(user_id)
        """)

        await db.commit()


@beartype
async def check_database_health(db_path: Path) -> bool:
    """Проверить доступность и целостность базы данных.

    Args:
        db_path: Путь к файлу базы данных

    Returns:
        bool: True если база данных в порядке
    """
    try:
        if not db_path.exists():
            return False

        async with aiosqlite.connect(db_path) as db:
            # Простой тестовый запрос
            async with db.execute("SELECT 1") as cursor:
                result = await cursor.fetchone()
                return result is not None
    except Exception:
        return False
