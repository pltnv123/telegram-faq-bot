"""Расчёт метрик CX/операционки: FRT, FCR, CSAT, containment rate."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import aiosqlite
from beartype import beartype


class MetricsCalculator:
    """Калькулятор метрик."""

    @beartype
    def __init__(self, db_path: Path) -> None:
        """Инициализация."""
        self.db_path = db_path

    @beartype
    async def calculate_frt_p50(self, days: int = 7) -> float:
        """Рассчитать First Response Time P50 (медиана).

        Args:
            days: Период в днях

        Returns:
            float: FRT P50 в секундах
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT event_data FROM events
                WHERE event_type = 'first_bot_response' AND timestamp > ?
                """,
                (cutoff,),
            ) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            return 0.0

        response_times = []
        for row in rows:
            data = json.loads(row[0])
            if "response_time_ms" in data:
                response_times.append(data["response_time_ms"] / 1000)  # в секундах

        if not response_times:
            return 0.0

        response_times.sort()
        median_idx = len(response_times) // 2
        return response_times[median_idx]

    @beartype
    async def calculate_containment_rate(self, days: int = 7) -> float:
        """Рассчитать containment rate (% диалогов без handoff).

        Args:
            days: Период в днях

        Returns:
            float: Containment rate (0.0 - 1.0)
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        async with aiosqlite.connect(self.db_path) as db:
            # Всего диалогов
            async with db.execute(
                """
                SELECT COUNT(DISTINCT user_id) FROM events
                WHERE event_type = 'conversation_started' AND timestamp > ?
                """,
                (cutoff,),
            ) as cursor:
                row = await cursor.fetchone()
                total = row[0] if row else 0

            if total == 0:
                return 0.0

            # Диалогов с handoff
            async with db.execute(
                """
                SELECT COUNT(DISTINCT user_id) FROM events
                WHERE event_type = 'ticket_created' AND timestamp > ?
                """,
                (cutoff,),
            ) as cursor:
                row = await cursor.fetchone()
                handoff = row[0] if row else 0

        return (total - handoff) / total if total > 0 else 0.0

    @beartype
    async def get_weekly_report(self, week_offset: int = 0) -> dict:
        """Получить еженедельный отчёт.

        Args:
            week_offset: Смещение недель (0=текущая, 1=прошлая)

        Returns:
            dict: Отчёт с метриками
        """
        days = 7
        frt = await self.calculate_frt_p50(days)
        containment = await self.calculate_containment_rate(days)

        return {
            "period": f"{datetime.now().year}-W{datetime.now().isocalendar()[1] - week_offset}",
            "frt_p50_seconds": round(frt, 1),
            "containment_rate": round(containment, 2),
            "handoff_rate": round(1 - containment, 2),
        }
