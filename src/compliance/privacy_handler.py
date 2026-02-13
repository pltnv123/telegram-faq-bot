"""Обработчик privacy requests - удаление, экспорт, исправление данных.

Реализует базовые требования GDPR Article 15-20 и 152-ФЗ.
"""

from __future__ import annotations

from pathlib import Path

from beartype import beartype

from src.handoff.ticket_manager import Ticket, TicketManager, TicketType


class PrivacyRequestHandler:
    """Обработчик запросов по персональным данным."""

    @beartype
    def __init__(self, ticket_manager: TicketManager) -> None:
        """Инициализация.

        Args:
            ticket_manager: Менеджер тикетов для эскалации
        """
        self.ticket_manager = ticket_manager

    @beartype
    async def handle_delete_request(
        self, user_id: int, contact: str, conversation_history: list
    ) -> Ticket:
        """Обработать запрос на удаление данных (right to erasure, GDPR Art. 17).

        Args:
            user_id: ID пользователя
            contact: Контакт для связи
            conversation_history: История диалога

        Returns:
            Ticket: Созданный тикет для обработки
        """
        from src.nlu.slot_extractor import SlotCollection

        slots = SlotCollection()
        slots.set_value("request_type", "delete_data")

        ticket = await self.ticket_manager.create_ticket(
            ticket_type=TicketType.PRIVACY,
            user_id=user_id,
            customer_contact=contact,
            summary=f"Запрос на удаление персональных данных пользователя {user_id}",
            slots=slots,
            conversation_history=conversation_history,
            requested_action="delete_user_data",
        )

        return ticket

    @beartype
    async def handle_export_request(
        self, user_id: int, contact: str, conversation_history: list
    ) -> Ticket:
        """Обработать запрос на выгрузку данных (right to data portability, GDPR Art. 20).

        Args:
            user_id: ID пользователя
            contact: Контакт
            conversation_history: История

        Returns:
            Ticket: Созданный тикет
        """
        from src.nlu.slot_extractor import SlotCollection

        slots = SlotCollection()
        slots.set_value("request_type", "export_data")

        ticket = await self.ticket_manager.create_ticket(
            ticket_type=TicketType.PRIVACY,
            user_id=user_id,
            customer_contact=contact,
            summary=f"Запрос на выгрузку данных пользователя {user_id}",
            slots=slots,
            conversation_history=conversation_history,
            requested_action="export_user_data",
        )

        return ticket

    @beartype
    async def handle_correction_request(
        self, user_id: int, contact: str, details: str, conversation_history: list
    ) -> Ticket:
        """Обработать запрос на исправление данных (right to rectification, GDPR Art. 16).

        Args:
            user_id: ID пользователя
            contact: Контакт
            details: Что нужно исправить
            conversation_history: История

        Returns:
            Ticket: Созданный тикет
        """
        from src.nlu.slot_extractor import SlotCollection

        slots = SlotCollection()
        slots.set_value("request_type", "correct_data")
        slots.set_value("correction_details", details)

        ticket = await self.ticket_manager.create_ticket(
            ticket_type=TicketType.PRIVACY,
            user_id=user_id,
            customer_contact=contact,
            summary=f"Запрос на исправление данных: {details[:100]}",
            slots=slots,
            conversation_history=conversation_history,
            requested_action="correct_user_data",
        )

        return ticket

    @beartype
    def get_privacy_notice(self) -> str:
        """Получить уведомление о сборе данных (transparency obligation).

        Returns:
            str: Текст уведомления
        """
        return (
            "Я собираю историю диалогов для улучшения качества обслуживания.\n\n"
            "Вы можете:\n"
            "• Запросить удаление данных командой /privacy\n"
            "• Получить копию своих данных\n"
            "• Исправить неточности\n\n"
            "Подробнее о защите данных: [ссылка на политику]"
        )

    @beartype
    def get_privacy_menu_text(self) -> str:
        """Получить текст меню /privacy.

        Returns:
            str: Текст меню
        """
        return (
            "Управление вашими данными:\n\n"
            "1. Удалить историю диалогов\n"
            "2. Выгрузить данные (запрос к менеджеру)\n"
            "3. Исправить данные\n"
            "4. Связаться по вопросам данных\n\n"
            "Выберите действие или напишите запрос."
        )
