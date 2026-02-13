"""Отслеживание SLA для тикетов."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import aiosqlite
from beartype import beartype


class SLATracker:
    """Трекер SLA для тикетов."""

    @beartype
    def __init__(self, db_path: Path) -> None:
        """Инициализация."""
        self.db_path = db_path

    @beartype
    async def get_overdue_tickets(self) -> list[dict[str, str | int]]:
        """Получить список просроченных тикетов.

        Returns:
            list: Список просроченных тикетов
        """
        now = datetime.now().isoformat()

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT id, ticket_type, priority, summary, sla_deadline_at
                FROM tickets
                WHERE status = 'open' AND sla_deadline_at < ?
                ORDER BY priority, sla_deadline_at
                """,
                (now,),
            ) as cursor:
                rows = await cursor.fetchall()

        overdue = []
        for row in rows:
            overdue.append({
                "ticket_id": row[0],
                "ticket_type": row[1],
                "priority": row[2],
                "summary": row[3],
                "sla_deadline_at": row[4],
            })

        return overdue

    @beartype
    async def get_sla_metrics(self, days: int = 7) -> dict[str, float]:
        """Получить метрики по SLA за период.

        Args:
            days: Период в днях

        Returns:
            dict: Метрики SLA
        """
        # Упрощённая реализация для MVP
        overdue = await self.get_overdue_tickets()

        return {
            "overdue_count": len(overdue),
            "sla_compliance_rate": 0.95,  # Заглушка
        }
