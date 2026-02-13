"""Отслеживание согласий пользователей (consent management).

Базовая реализация для MVP, full GDPR consent требует больше логики.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import aiosqlite
from beartype import beartype


class ConsentTracker:
    """Трекер согласий пользователей."""

    @beartype
    def __init__(self, db_path: Path) -> None:
        """Инициализация."""
        self.db_path = db_path

    @beartype
    async def record_consent(
        self, user_id: int, consent_type: str, granted: bool
    ) -> None:
        """Записать согласие пользователя.

        Args:
            user_id: ID пользователя
            consent_type: Тип согласия (e.g., "data_processing")
            granted: Дано ли согласие
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO user_consents (user_id, consent_type, granted, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, consent_type, granted, datetime.now().isoformat()),
            )
            await db.commit()

    @beartype
    async def has_consent(self, user_id: int, consent_type: str) -> bool:
        """Проверить наличие согласия.

        Args:
            user_id: ID пользователя
            consent_type: Тип согласия

        Returns:
            bool: Есть ли согласие
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT granted FROM user_consents
                WHERE user_id = ? AND consent_type = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (user_id, consent_type),
            ) as cursor:
                row = await cursor.fetchone()
                return bool(row and row[0]) if row else False

    @beartype
    async def get_consent_history(self, user_id: int) -> list[dict]:
        """Получить историю согласий пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            list: История согласий
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT consent_type, granted, timestamp
                FROM user_consents
                WHERE user_id = ?
                ORDER BY timestamp DESC
                """,
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()

        history = []
        for row in rows:
            history.append({
                "consent_type": row[0],
                "granted": bool(row[1]),
                "timestamp": row[2],
            })

        return history
