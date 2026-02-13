"""Управление контекстом диалогов пользователей."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import aiosqlite
from beartype import beartype


@beartype
@dataclass(frozen=True)
class Message:
    """Сообщение в диалоге."""

    role: str  # 'user' или 'assistant'
    content: str
    timestamp: datetime


@beartype
class ConversationContext:
    """Управление контекстом диалогов."""

    def __init__(self, db_path: Path) -> None:
        """Инициализация менеджера контекста.

        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path

    async def save_user(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> None:
        """Сохранить или обновить информацию о пользователе.

        Args:
            user_id: Telegram ID пользователя
            username: Username пользователя
            first_name: Имя пользователя
            last_name: Фамилия пользователя
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    last_active = CURRENT_TIMESTAMP
                """,
                (user_id, username, first_name, last_name),
            )
            await db.commit()

    async def save_message(
        self,
        user_id: int,
        role: str,
        content: str,
        tokens_used: int = 0,
    ) -> None:
        """Сохранить сообщение в истории диалога.

        Args:
            user_id: Telegram ID пользователя
            role: Роль отправителя ('user' или 'assistant')
            content: Текст сообщения
            tokens_used: Количество использованных токенов (для AI)
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO messages (user_id, role, content, tokens_used)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, role, content, tokens_used),
            )
            await db.commit()

    async def get_context(
        self,
        user_id: int,
        limit: int = 10,
    ) -> list[Message]:
        """Получить историю диалога пользователя.

        Args:
            user_id: Telegram ID пользователя
            limit: Максимальное количество сообщений

        Returns:
            list[Message]: Список сообщений (от старых к новым)
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT role, content, timestamp
                FROM messages
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (user_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()

        # Преобразовать в список Message (переверну��ть порядок)
        messages = [
            Message(
                role=row[0],
                content=row[1],
                timestamp=datetime.fromisoformat(row[2]),
            )
            for row in reversed(rows)
        ]

        return messages

    async def clear_context(self, user_id: int) -> None:
        """Очистить историю диалога пользователя.

        Args:
            user_id: Telegram ID пользователя
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM messages WHERE user_id = ?",
                (user_id,),
            )
            await db.commit()

    async def cleanup_old_messages(self, days: int = 7) -> int:
        """Удалить старые сообщения.

        Args:
            days: Удалить сообщения старше N дней

        Returns:
            int: Количество удаленных сообщений
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM messages WHERE timestamp < ?",
                (cutoff_date.isoformat(),),
            )
            deleted = cursor.rowcount
            await db.commit()

        return deleted

    async def get_user_stats(self, user_id: int) -> dict[str, int | datetime | None]:
        """Получить статистику пользователя.

        Args:
            user_id: Telegram ID пользователя

        Returns:
            dict: Статистика (total_messages, first_seen, last_active)
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Количество сообщений
            async with db.execute(
                "SELECT COUNT(*) FROM messages WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                total_messages = row[0] if row else 0

            # Информация о пользователе
            async with db.execute(
                "SELECT first_seen, last_active FROM users WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    first_seen = datetime.fromisoformat(row[0])
                    last_active = datetime.fromisoformat(row[1])
                else:
                    first_seen = None
                    last_active = None

        return {
            "total_messages": total_messages,
            "first_seen": first_seen,
            "last_active": last_active,
        }
