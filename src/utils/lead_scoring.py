"""Система оценки и квалификации лидов для продающего бота."""

from __future__ import annotations

from beartype import beartype

from src.database.context import Message


@beartype
def calculate_lead_score(
    user_message: str,
    conversation_history: list[Message],
    intent: str,
) -> int:
    """Оценить температуру лида от 0 до 10.

    Args:
        user_message: Текущее сообщение пользователя
        conversation_history: История предыдущих сообщений
        intent: Определенное намерение (pricing, services, order и т.д.)

    Returns:
        int: Оценка от 0 (холодный) до 10 (горячий)
    """
    score = 0
    message_lower = user_message.lower()

    # Сильные сигналы покупки (+4 балла)
    hot_keywords = [
        "заказать",
        "купить",
        "начать",
        "оформить",
        "записаться",
        "хочу заказать",
        "готов заказать",
        "когда начнем",
        "договор",
        "подать заявку",
        "оплатить",
        "где оплата",
    ]
    if any(kw in message_lower for kw in hot_keywords):
        score += 4

    # Средние сигналы интереса (+2 балла)
    warm_keywords = [
        "цена",
        "стоимость",
        "срок",
        "как работает",
        "гарантия",
        "результат",
        "кейс",
        "пример",
        "отзыв",
        "портфолио",
        "опыт",
        "сколько стоит",
    ]
    if any(kw in message_lower for kw in warm_keywords):
        score += 2

    # Конкретные намерения (+2 балла)
    if intent in ["pricing", "services", "order"]:
        score += 2
    elif intent == "contacts":
        score += 3  # Хочет связаться = горячий

    # Длина диалога (чем больше, тем теплее)
    messages_count = len(conversation_history)
    if messages_count >= 5:
        score += 2
    elif messages_count >= 3:
        score += 1

    # Детальные вопросы показывают заинтересованность (+1 балл)
    if len(user_message) > 50:
        score += 1

    # Вопросы о конкретных деталях (+1 балл)
    detail_keywords = [
        "для меня",
        "в моем случае",
        "мой проект",
        "моя задача",
        "мне нужно",
        "у меня",
    ]
    if any(kw in message_lower for kw in detail_keywords):
        score += 1

    return min(score, 10)  # Максимум 10


@beartype
def detect_funnel_stage(
    conversation_history: list[Message],
    lead_score: int,
) -> str:
    """Определить текущий этап воронки продаж.

    Args:
        conversation_history: История сообщений
        lead_score: Оценка температуры лида

    Returns:
        str: Этап воронки (AWARENESS, INTEREST, CONSIDERATION, DECISION)
    """
    # Принятие решения - готов заказать
    if lead_score >= 7:
        return "DECISION"

    # Рассмотрение вариантов - сравнивает, думает
    if lead_score >= 4:
        return "CONSIDERATION"

    # Первое сообщение - знакомство
    if len(conversation_history) == 0:
        return "AWARENESS"

    # Проявление интереса - задает вопросы
    return "INTEREST"


@beartype
def get_lead_temperature_label(lead_score: int) -> str:
    """Получить текстовую метку температуры лида.

    Args:
        lead_score: Оценка от 0 до 10

    Returns:
        str: COLD, WARM или HOT
    """
    if lead_score <= 3:
        return "COLD"
    elif lead_score <= 6:
        return "WARM"
    else:
        return "HOT"
