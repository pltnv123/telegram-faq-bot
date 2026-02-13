"""Оценка качества диалога (10-балльная карточка)."""

from __future__ import annotations

from dataclasses import dataclass

from beartype import beartype


@dataclass
class DialogScore:
    """Оценка диалога."""

    intent_understanding: int  # 0-2
    slot_collection: int  # 0-2
    response_usefulness: int  # 0-2
    compliance: int  # 0-2
    tone_clarity: int  # 0-2

    @beartype
    def total(self) -> int:
        """Общая оценка."""
        return (
            self.intent_understanding
            + self.slot_collection
            + self.response_usefulness
            + self.compliance
            + self.tone_clarity
        )


# Стоп-ошибки (автоматический fail)
STOP_ERRORS = [
    "hallucinated_price",  # Выдуманная цена
    "hallucinated_guarantee",  # Выдуманная гарантия
    "unauthorized_refund_promise",  # Обещание возврата без политики
    "pii_disclosure",  # Раскрытие данных третьей стороне
    "ignored_privacy_request",  # Игнор privacy request
    "argued_with_complaint",  # Спор с клиентом в претензии
]


@beartype
def has_stop_error(dialog_text: str, bot_response: str) -> tuple[bool, str | None]:
    """Проверить наличие стоп-ошибки.

    Args:
        dialog_text: Текст диалога
        bot_response: Ответ бота

    Returns:
        tuple[bool, str | None]: (есть ли ошибка, какая)
    """
    # Упрощённая проверка (в production нужны более сложные правила)

    # Проверка на выдумку цены
    if "руб" in bot_response and "от" not in bot_response and "до" not in bot_response:
        # Может быть точная цена без "от" или "до" - это подозрительно
        pass

    # Проверка на игнор privacy request
    if "удалите данные" in dialog_text.lower() and "регистр" not in bot_response.lower():
        return True, "ignored_privacy_request"

    return False, None
