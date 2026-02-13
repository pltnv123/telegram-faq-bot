"""Обработчик команды /privacy для управления персональными данными."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from beartype import beartype

from src.compliance.privacy_handler import PrivacyRequestHandler
from src.database.context import ConversationContext
from src.handoff.ticket_manager import TicketManager

router = Router()


@router.message(Command("privacy"))
@beartype
async def handle_privacy_command(
    message: Message, context: ConversationContext
) -> None:
    """Обработать команду /privacy.

    Args:
        message: Сообщение от пользователя
        context: Менеджер контекста
    """
    if not message.from_user:
        return

    user_id = message.from_user.id

    # Текст меню privacy
    privacy_menu = (
        "🔒 Управление вашими данными:\n\n"
        "1️⃣ Удалить историю диалогов\n"
        "2️⃣ Выгрузить данные (запрос к менеджеру)\n"
        "3️⃣ Связаться по вопросам данных\n\n"
        "Выберите действие:\n"
        "• Напишите 'удалить данные' для удаления\n"
        "• Напишите 'выгрузить данные' для экспорта\n"
        "• Или свяжитесь: info@example.com"
    )

    await message.answer(privacy_menu, parse_mode=None)


@router.message(Command("delete_data"))
@beartype
async def handle_delete_data_command(
    message: Message, context: ConversationContext
) -> None:
    """Обработать команду /delete_data (удаление данных).

    Args:
        message: Сообщение
        context: Контекст
    """
    if not message.from_user:
        return

    user_id = message.from_user.id

    # Удалить историю диалогов
    await context.clear_context(user_id)

    response = (
        "✅ История диалогов удалена.\n\n"
        "Если хотите удалить все данные (включая заказы, если есть), "
        "свяжитесь с нами: info@example.com"
    )

    await message.answer(response, parse_mode=None)
