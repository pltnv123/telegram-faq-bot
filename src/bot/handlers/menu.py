"""Обработчики интерактивного меню (callback кнопок)."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from beartype import beartype

from src.bot.keyboards import (
    back_to_menu_keyboard,
    faq_categories_keyboard,
    main_menu_keyboard,
    services_keyboard,
)
from src.database.context import ConversationContext
from src.knowledge.faq_loader import KnowledgeBase

router = Router()


@router.callback_query(F.data == "mnu")
@beartype
async def callback_main_menu(
    callback: CallbackQuery,
    knowledge_base: KnowledgeBase,
) -> None:
    """Показать главное меню.

    Args:
        callback: Callback от кнопки
        knowledge_base: База знаний
    """
    if not callback.message:
        return

    menu_text = f"""📋 Меню навигации

Выберите интересующий раздел или продолжите задавать вопросы текстом.

💡 Совет: Я понимаю обычные вопросы лучше, чем навигацию по меню!
"""

    await callback.message.edit_text(
        text=menu_text,
        reply_markup=main_menu_keyboard(),
        parse_mode=None,
    )
    await callback.answer()


@router.callback_query(F.data.in_(["srv", "services"]))
@beartype
async def callback_services(
    callback: CallbackQuery,
    knowledge_base: KnowledgeBase,
) -> None:
    """Показать список услуг.

    Args:
        callback: Callback от кнопки
        knowledge_base: База знаний
    """
    if not callback.message:
        return

    text = f"**📋 Наши услуги:**\n\n{knowledge_base.company.description}\n\nВыберите услугу для подробной информации:"

    await callback.message.edit_text(
        text=text,
        reply_markup=services_keyboard(knowledge_base),
    )
    await callback.answer()


@router.callback_query(F.data == "prc")
@beartype
async def callback_pricing(
    callback: CallbackQuery,
    knowledge_base: KnowledgeBase,
) -> None:
    """Показать информацию о ценах.

    Args:
        callback: Callback от кнопки
        knowledge_base: База знаний
    """
    if not callback.message:
        return

    text = "**💰 Наши цены:**\n\n"
    for service in knowledge_base.services:
        text += f"**{service.name}**\n"
        text += f"Цена: {service.price}\n"
        text += f"Срок: {service.duration}\n\n"

    text += "Для точной оценки свяжитесь с нами!"

    await callback.message.edit_text(
        text=text,
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("s:"))
@beartype
async def callback_service_detail(
    callback: CallbackQuery,
    knowledge_base: KnowledgeBase,
) -> None:
    """Показать детали услуги.

    Args:
        callback: Callback от кнопки
        knowledge_base: База знаний
    """
    if not callback.message or not callback.data:
        return

    # Извлечь индекс услуги из callback_data
    try:
        service_idx = int(callback.data.split(":")[1]) - 1
        if 0 <= service_idx < len(knowledge_base.services):
            service = knowledge_base.services[service_idx]
        else:
            await callback.answer("Услуга не найдена", show_alert=True)
            return
    except (ValueError, IndexError):
        await callback.answer("Ошибка данных", show_alert=True)
        return

    # Форматировать информацию об услуге
    text = f"""**{service.name}**

{service.description}

💰 **Цена:** {service.price}
⏱ **Срок:** {service.duration}

**Преимущества:**
"""
    for benefit in service.benefits:
        text += f"✓ {benefit}\n"

    text += f"\n**Хотите заказать?**\nСвяжитесь с нами:\n"
    text += f"📞 {knowledge_base.company.phone}\n"
    text += f"📧 {knowledge_base.company.email}\n"
    text += f"💬 {knowledge_base.company.telegram}"

    await callback.message.edit_text(
        text=text,
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "faq")
@beartype
async def callback_faq(
    callback: CallbackQuery,
    knowledge_base: KnowledgeBase,
) -> None:
    """Показать категории FAQ.

    Args:
        callback: Callback от кнопки
        knowledge_base: База знаний
    """
    if not callback.message:
        return

    text = "**❓ Частые вопросы**\n\nВыберите категорию:"

    await callback.message.edit_text(
        text=text,
        reply_markup=faq_categories_keyboard(knowledge_base),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fq:"))
@beartype
async def callback_faq_category(
    callback: CallbackQuery,
    knowledge_base: KnowledgeBase,
) -> None:
    """Показать вопросы из категории FAQ.

    Args:
        callback: Callback от кнопки
        knowledge_base: База знаний
    """
    if not callback.message or not callback.data:
        return

    # Извлечь категорию из callback_data
    category_code = callback.data.split(":")[1]
    
    # Маппинг коротких кодов в полные названия категорий
    code_to_category = {
        "g": "general",
        "p": "pricing",
        "t": "timing",
    }
    
    category = code_to_category.get(category_code, category_code)
    faq_items = knowledge_base.get_faq_by_category(category)

    if not faq_items:
        await callback.answer("Вопросы не найдены", show_alert=True)
        return

    # Форматировать список вопросов
    category_names = {
        "general": "Общие вопросы",
        "pricing": "Цены и оплата",
        "timing": "Сроки",
    }
    category_name = category_names.get(category, category.title())

    text = f"**{category_name}**\n\n"
    for item in faq_items:
        text += f"**Q:** {item.question}\n"
        text += f"**A:** {item.answer}\n\n"

    await callback.message.edit_text(
        text=text,
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.in_(["cnt", "contacts"]))
@beartype
async def callback_contacts(
    callback: CallbackQuery,
    knowledge_base: KnowledgeBase,
) -> None:
    """Показать контакты компании.

    Args:
        callback: Callback от кнопки
        knowledge_base: База знаний
    """
    if not callback.message:
        return

    text = f"""**📞 Контакты**

**{knowledge_base.company.name}**
{knowledge_base.company.description}

🌐 Сайт: {knowledge_base.company.website}
📞 Телефон: {knowledge_base.company.phone}
📧 Email: {knowledge_base.company.email}
💬 Telegram: {knowledge_base.company.telegram}

Будем рады помочь вам!
"""

    await callback.message.edit_text(
        text=text,
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "sts")
@beartype
async def callback_stats(
    callback: CallbackQuery,
    context: ConversationContext,
) -> None:
    """Показать статистику пользователя.

    Args:
        callback: Callback от кнопки
        context: Менеджер контекста
    """
    if not callback.message or not callback.from_user:
        return

    stats = await context.get_user_stats(callback.from_user.id)

    if stats["first_seen"]:
        first_seen_str = stats["first_seen"].strftime("%d.%m.%Y %H:%M")
    else:
        first_seen_str = "неизвестно"

    stats_text = f"""**📊 Ваша статистика:**

💬 Всего сообщений: {stats['total_messages']}
📅 Первое обращение: {first_seen_str}

Спасибо что пользуетесь нашим ботом!
"""

    await callback.message.edit_text(
        text=stats_text,
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()
