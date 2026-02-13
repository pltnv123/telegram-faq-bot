"""Менеджер тикетов для handoff к менеджерам.

Создаёт, сохраняет и управляет тикетами для эскалации.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

import aiosqlite
from beartype import beartype

if TYPE_CHECKING:
    from src.database.context import Message
    from src.nlu.slot_extractor import SlotCollection


class TicketType(str, Enum):
    """Типы тикетов."""

    SALES_LEAD = "sales_lead"
    REFUND = "refund"
    COMPLAINT = "complaint"
    LEGAL = "legal"
    PRIVACY = "privacy"


class Priority(str, Enum):
    """Приоритеты тикетов."""

    P1 = "P1"  # Критический (privacy, legal, refund)
    P2 = "P2"  # Высокий (complaint, hot lead)
    P3 = "P3"  # Нормальный (sales lead)


@dataclass
class Ticket:
    """Тикет для handoff."""

    ticket_type: TicketType
    priority: Priority
    customer_contact: str
    summary: str
    context: dict  # Слоты + последние сообщения
    requested_action: str
    sla_deadline_at: datetime
    created_at: datetime
    user_id: int
    status: str = "open"
    ticket_id: int | None = None

    @beartype
    def to_json(self) -> str:
        """Сериализовать тикет в JSON для CRM интеграции."""
        data = asdict(self)
        # Преобразовать datetime в ISO format
        data["sla_deadline_at"] = self.sla_deadline_at.isoformat()
        data["created_at"] = self.created_at.isoformat()
        # Преобразовать enum в строки
        data["ticket_type"] = self.ticket_type.value
        data["priority"] = self.priority.value
        return json.dumps(data, ensure_ascii=False, indent=2)


class TicketManager:
    """Менеджер тикетов."""

    @beartype
    def __init__(self, db_path: Path) -> None:
        """Инициализация.

        Args:
            db_path: Путь к БД
        """
        self.db_path = db_path

    @beartype
    async def create_ticket(
        self,
        ticket_type: TicketType,
        user_id: int,
        customer_contact: str,
        summary: str,
        slots: SlotCollection,
        conversation_history: list[Message],
        requested_action: str = "",
    ) -> Ticket:
        """Создать новый тикет.

        Args:
            ticket_type: Тип тикета
            user_id: ID пользователя
            customer_contact: Контакт клиента
            summary: Краткое описание
            slots: Собранные слоты
            conversation_history: История диалога
            requested_action: Запрошенное действие

        Returns:
            Ticket: Созданный тикет
        """
        # Определить приоритет по типу
        priority = self._get_priority_by_type(ticket_type)

        # Определить SLA deadline
        sla_deadline = self._calculate_sla_deadline(priority)

        # Создать контекст
        context = {
            "slots": {name: slots.get_value(name) for name in slots.slots.keys()},
            "last_messages": [
                {"role": msg.role, "content": msg.content[:200]}
                for msg in conversation_history[-5:]
            ],
        }

        # Создать тикет
        ticket = Ticket(
            ticket_type=ticket_type,
            priority=priority,
            customer_contact=customer_contact,
            summary=summary,
            context=context,
            requested_action=requested_action or self._default_action(ticket_type),
            sla_deadline_at=sla_deadline,
            created_at=datetime.now(),
            user_id=user_id,
            status="open",
        )

        # Сохранить в БД
        ticket_id = await self._save_to_db(ticket)
        ticket.ticket_id = ticket_id

        # Экспорт в JSON (опционально для CRM)
        await self._export_to_json(ticket)

        return ticket

    @beartype
    def _get_priority_by_type(self, ticket_type: TicketType) -> Priority:
        """Определить приоритет по типу тикета."""
        priority_map = {
            TicketType.PRIVACY: Priority.P1,
            TicketType.LEGAL: Priority.P1,
            TicketType.REFUND: Priority.P1,
            TicketType.COMPLAINT: Priority.P2,
            TicketType.SALES_LEAD: Priority.P3,
        }
        return priority_map.get(ticket_type, Priority.P3)

    @beartype
    def _calculate_sla_deadline(self, priority: Priority) -> datetime:
        """Рассчитать SLA deadline."""
        now = datetime.now()

        sla_hours = {
            Priority.P1: 4,  # 4 часа для критичных
            Priority.P2: 24,  # 24 часа для высоких
            Priority.P3: 72,  # 72 часа для нормальных
        }

        hours = sla_hours.get(priority, 72)
        return now + timedelta(hours=hours)

    @beartype
    def _default_action(self, ticket_type: TicketType) -> str:
        """Дефолтное действие по типу тикета."""
        actions = {
            TicketType.PRIVACY: "process_data_request",
            TicketType.LEGAL: "legal_review",
            TicketType.REFUND: "process_refund",
            TicketType.COMPLAINT: "investigate_complaint",
            TicketType.SALES_LEAD: "call_back",
        }
        return actions.get(ticket_type, "review")

    @beartype
    async def _save_to_db(self, ticket: Ticket) -> int:
        """Сохранить тикет в БД."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO tickets (
                    user_id, ticket_type, priority, summary,
                    context_json, requested_action, sla_deadline_at,
                    status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket.user_id,
                    ticket.ticket_type.value,
                    ticket.priority.value,
                    ticket.summary,
                    json.dumps(ticket.context, ensure_ascii=False),
                    ticket.requested_action,
                    ticket.sla_deadline_at.isoformat(),
                    ticket.status,
                    ticket.created_at.isoformat(),
                ),
            )
            await db.commit()
            return cursor.lastrowid or 0

    @beartype
    async def _export_to_json(self, ticket: Ticket) -> None:
        """Экспортировать тикет в JSON файл для CRM интеграции."""
        export_dir = Path("data/tickets")
        export_dir.mkdir(exist_ok=True)

        filename = f"ticket_{ticket.ticket_id}_{ticket.created_at.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = export_dir / filename

        filepath.write_text(ticket.to_json(), encoding="utf-8")

    @beartype
    async def get_ticket(self, ticket_id: int) -> Ticket | None:
        """Получить тикет по ID."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None

                # Парсинг row в Ticket
                # (упрощённая версия, в production нужен полный парсинг)
                return None  # TODO: implement

    @beartype
    async def update_status(self, ticket_id: int, new_status: str) -> None:
        """Обновить статус тикета."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE tickets SET status = ? WHERE id = ?", (new_status, ticket_id)
            )
            await db.commit()
