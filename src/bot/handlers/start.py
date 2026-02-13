"""Обработчики команд /start, /help, /reset, /menu."""

from __future__ import annotations

import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from beartype import beartype

from src.bot.keyboards import main_menu_keyboard
from src.database.context import ConversationContext
from src.knowledge.faq_loader import KnowledgeBase

router = Router()


@router.message(Command("start"))
@beartype
async def cmd_start(
    message: Message,
    knowledge_base: KnowledgeBase,
    context: ConversationContext,
) -> None:
    """Обработать команду /start.

    Args:
        message: Сообщение от пользователя
        knowledge_base: База знаний
        context: Менеджер контекста диалогов
    """
    if not message.from_user:
        return

    # Сохранить информацию о пользователе
    await context.save_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    # Новый conversational-first приветственный текст
    welcome_text = f"""Привет! Я AI-ассистент компании {knowledge_base.company.name}.

Я отвечу на любой вопрос о наших услугах. Просто напишите мне!

Примеры вопросов:
💬 "Какие у вас услуги?"
💬 "Сколько стоит консультация?"
💬 "Как быстро вы работаете?"
💬 "Как с вами связаться?"

Или используйте команду /menu для навигации по разделам.
"""

    # Отправить приветствие БЕЗ кнопок вообще
    from src.bot.keyboards import remove_keyboard
    await message.answer(
        text=welcome_text, 
        reply_markup=remove_keyboard(),
        parse_mode=None  # Отключаем парсинг форматирования
    )


@router.message(Command("help"))
@beartype
async def cmd_help(message: Message) -> None:
    """Обработать команду /help.

    Args:
        message: Сообщение от пользователя
    """
    help_text = """🤖 **Как пользоваться ботом**

**Главное:**
Просто пишите мне вопросы обычным текстом! Я понимаю естественный язык.

**Примеры вопросов:**
• "Какие у вас услуги?"
• "Сколько стоит консультация?"
• "Как быстро вы работаете?"
• "Есть ли у вас техподдержка?"

**Команды:**
/start - Начать работу
/menu - Показать навигацию по разделам
/reset - Начать диалог заново
/stats - Показать статистику

**Возможности:**
✓ Я помню контекст нашего разговора
✓ Могу отвечать на уточняющие вопросы
✓ Работаю с AI для умных ответов
✓ Предлагаю контекстные подсказки

**Quick Reply кнопки:**
Под моими ответами появляются кнопки для быстрых действий. Но вы всегда можете писать свои вопросы текстом!
"""
    await message.answer(text=help_text)


@router.message(Command("reset"))
@beartype
async def cmd_reset(
    message: Message,
    context: ConversationContext,
) -> None:
    """Обработать команду /reset - очистить историю диалога.

    Args:
        message: Сообщение от пользователя
        context: Менеджер контекста диалогов
    """
    if not message.from_user:
        return

    # Очистить контекст
    await context.clear_context(message.from_user.id)

    await message.answer(
        text="✅ История диалога очищена. Начнем заново!\n\n"
        "Чем могу помочь?",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("stats"))
@beartype
async def cmd_stats(
    message: Message,
    context: ConversationContext,
) -> None:
    """Показать статистику пользователя.

    Args:
        message: Сообщение от пользователя
        context: Менеджер контекста диалогов
    """
    if not message.from_user:
        return

    stats = await context.get_user_stats(message.from_user.id)

    if stats["first_seen"]:
        first_seen_str = stats["first_seen"].strftime("%d.%m.%Y %H:%M")
    else:
        first_seen_str = "неизвестно"

    stats_text = f"""
📊 **Ваша статистика:**

💬 Всего сообщений: {stats['total_messages']}
📅 Первое обращение: {first_seen_str}

Спасибо что пользуетесь нашим ботом!
"""
    await message.answer(text=stats_text)


@router.message(Command("menu"))
@beartype
async def cmd_menu(
    message: Message,
    knowledge_base: KnowledgeBase,
) -> None:
    """Показать меню навигации с inline кнопками.

    Args:
        message: Сообщение от пользователя
        knowledge_base: База знаний
    """
    menu_text = f"""📋 **Меню навигации**

Выберите интересующий раздел или продолжите задавать вопросы текстом.

💡 **Совет:** Я понимаю обычные вопросы лучше, чем навигацию по меню! Просто напишите что вас интересует.
"""

    await message.answer(
        text=menu_text,
        reply_markup=main_menu_keyboard(),
    )
