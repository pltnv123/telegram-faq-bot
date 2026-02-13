"""Telegram клавиатуры и кнопки."""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from beartype import beartype

from src.knowledge.faq_loader import KnowledgeBase


@beartype
def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создать оптимизированное главное меню бота (2 колонки).

    Returns:
        InlineKeyboardMarkup: Клавиатура главного меню
    """
    buttons = [
        # Первая строка - 2 кнопки
        [
            InlineKeyboardButton(text="📋 Услуги", callback_data="srv"),
            InlineKeyboardButton(text="💰 Цены", callback_data="prc"),
        ],
        # Вторая строка - 2 кнопки
        [
            InlineKeyboardButton(text="❓ FAQ", callback_data="faq"),
            InlineKeyboardButton(text="📞 Контакты", callback_data="cnt"),
        ],
        # Третья строка - менее важные действия
        [InlineKeyboardButton(text="📊 Статистика", callback_data="sts")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@beartype
def services_keyboard(knowledge_base: KnowledgeBase) -> InlineKeyboardMarkup:
    """Создать клавиатуру со списком услуг.

    Args:
        knowledge_base: База знаний

    Returns:
        InlineKeyboardMarkup: Клавиатура с услугами
    """
    buttons = []

    # Добавить кнопку для каждой услуги (короткий callback_data)
    for idx, service in enumerate(knowledge_base.services, 1):
        buttons.append([
            InlineKeyboardButton(
                text=f"{service.name} ({service.price})",
                callback_data=f"s:{idx}",
            )
        ])

    # Кнопка назад
    buttons.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="mnu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@beartype
def faq_categories_keyboard(knowledge_base: KnowledgeBase) -> InlineKeyboardMarkup:
    """Создать клавиатуру с категориями FAQ.

    Args:
        knowledge_base: База знаний

    Returns:
        InlineKeyboardMarkup: Клавиатура с категориями
    """
    categories = knowledge_base.get_all_categories()
    buttons = []

    # Русские названия категорий с короткими callback
    category_mapping = {
        "general": ("Общие вопросы", "fq:g"),
        "pricing": ("Цены и оплата", "fq:p"),
        "timing": ("Сроки", "fq:t"),
    }

    for category in categories:
        display_name, callback_data = category_mapping.get(
            category, (category.title(), f"fq:{category[:1]}")
        )
        buttons.append([
            InlineKeyboardButton(
                text=display_name,
                callback_data=callback_data,
            )
        ])

    # Кнопка назад
    buttons.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="mnu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@beartype
def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Создать клавиатуру с кнопкой возврата в меню.

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой назад
    """
    buttons = [
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="mnu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@beartype
def contextual_quick_replies(context: str = "general", show_buttons: bool = True) -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    """Создать контекстные quick reply кнопки.

    Args:
        context: Контекст диалога (general, pricing, services, contacts, order)
        show_buttons: Показывать ли кнопки (False = убрать клавиатуру)

    Returns:
        ReplyKeyboardMarkup | ReplyKeyboardRemove: Клавиатура или удаление клавиатуры
    """
    # Если не нужно показывать кнопки - убрать клавиатуру
    if not show_buttons:
        return ReplyKeyboardRemove()
    
    # Минималистичные кнопки без лишних слов
    # Для общего контекста
    if context == "general":
        buttons = [
            [KeyboardButton(text="📋 Услуги"), KeyboardButton(text="💰 Цены")],
            [KeyboardButton(text="/menu")],
        ]
    # После ответа о ценах
    elif context == "pricing":
        buttons = [
            [KeyboardButton(text="📋 Услуги"), KeyboardButton(text="📞 Связаться")],
            [KeyboardButton(text="/menu")],
        ]
    # После ответа об услугах
    elif context == "services":
        buttons = [
            [KeyboardButton(text="💰 Цены"), KeyboardButton(text="📞 Связаться")],
            [KeyboardButton(text="/menu")],
        ]
    # После ответа о контактах
    elif context == "contacts":
        buttons = [
            [KeyboardButton(text="📋 Услуги"), KeyboardButton(text="💰 Цены")],
            [KeyboardButton(text="/menu")],
        ]
    # Когда хочет заказать
    elif context == "order":
        buttons = [
            [KeyboardButton(text="📞 Связаться")],
            [KeyboardButton(text="/menu")],
        ]
    else:
        buttons = [
            [KeyboardButton(text="/menu")],
        ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Напишите вопрос...",
    )


@beartype
def remove_keyboard() -> ReplyKeyboardRemove:
    """Убрать клавиатуру.

    Returns:
        ReplyKeyboardRemove: Объект для удаления клавиатуры
    """
    return ReplyKeyboardRemove()
