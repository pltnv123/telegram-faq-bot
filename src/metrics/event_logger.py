"""Логирование событий для метрик (FRT, FCR, CSAT, etc.)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import aiosqlite
from beartype import beartype


class EventLogger:
    """Логгер событий для расчёта метрик."""

    @beartype
    def __init__(self, db_path: Path) -> None:
        """Инициализация."""
        self.db_path = db_path

    @beartype
    async def log(self, user_id: int, event_type: str, event_data: dict | None = None) -> None:
        """Записать событие.

        Args:
            user_id: ID пользователя
            event_type: Тип события
            event_data: Дополнительные данные
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO events (user_id, event_type, event_data, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    event_type,
                    json.dumps(event_data or {}, ensure_ascii=False),
                    datetime.now().isoformat(),
                ),
            )
            await db.commit()

    @beartype
    async def log_conversation_started(self, user_id: int) -> None:
        """Записать начало диалога."""
        await self.log(user_id, "conversation_started")

    @beartype
    async def log_first_bot_response(self, user_id: int, response_time_ms: float) -> None:
        """Записать первый ответ бота."""
        await self.log(user_id, "first_bot_response", {"response_time_ms": response_time_ms})

    @beartype
    async def log_intent_classified(self, user_id: int, intent: str, confidence: float) -> None:
        """Записать классификацию интента."""
        await self.log(
            user_id, "intent_classified", {"intent": intent, "confidence": confidence}
        )

    @beartype
    async def log_funnel_stage_changed(self, user_id: int, old_stage: str, new_stage: str) -> None:
        """Записать изменение этапа воронки."""
        await self.log(
            user_id,
            "funnel_stage_changed",
            {"old_stage": old_stage, "new_stage": new_stage},
        )

    @beartype
    async def log_ticket_created(
        self, user_id: int, ticket_id: int, ticket_type: str, priority: str
    ) -> None:
        """Записать создание тикета."""
        await self.log(
            user_id,
            "ticket_created",
            {"ticket_id": ticket_id, "ticket_type": ticket_type, "priority": priority},
        )

    @beartype
    async def log_resolution(self, user_id: int, resolution_status: str) -> None:
        """Записать результат разрешения обращения."""
        await self.log(user_id, "resolution_completed", {"status": resolution_status})
