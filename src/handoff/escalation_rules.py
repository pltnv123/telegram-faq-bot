"""Правила эскалации - когда и как передавать менеджеру.

Определяет триггеры для автоматической эскалации.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from beartype import beartype

if TYPE_CHECKING:
    from src.nlu.intent_classifier import Intent


class EscalationRules:
    """Правила эскалации к менеджерам."""

    @beartype
    @staticmethod
    def should_escalate(intent: Intent, confidence: float = 0.0) -> tuple[bool, str]:
        """Проверить требуется ли эскалация.

        Args:
            intent: Классифицированный интент
            confidence: Уверенность NLU (опционально)

        Returns:
            tuple[bool, str]: (требуется ли эскалация, причина)
        """
        # Супер-приоритетные интенты ВСЕГДА эскалируются
        super_priority_groups = ["security", "privacy", "complaints"]

        if intent.group in super_priority_groups:
            return True, f"Критичный интент группы '{intent.group}'"

        # Низкая confidence при высокой цене ошибки
        if confidence < 0.3 and intent.group in ["transactions", "support"]:
            return True, "Низкая уверенность классификации при критичном запросе"

        # Явный запрос менеджера
        if intent.name == "human_handoff":
            return True, "Пользователь явно запросил менеджера"

        # Юридические вопросы
        if intent.name == "legal":
            return True, "Юридический вопрос требует специалиста"

        return False, ""

    @beartype
    @staticmethod
    def get_escalation_message(intent: Intent) -> str:
        """Получить сообщение для пользователя при эскалации.

        Args:
            intent: Интент

        Returns:
            str: Сообщение пользователю
        """
        messages = {
            "privacy": (
                "Ваш запрос по персональным данным зарегистрирован. "
                "Специалист свяжется с вами для верификации и выполнения запроса. "
                "Ожидаемый срок — до 30 дней."
            ),
            "refund_request": (
                "Ваш запрос на возврат принят. "
                "Менеджер свяжется с вами в течение 24 часов для уточнения деталей."
            ),
            "complaint": (
                "Ваша жалоба зарегистрирована. "
                "Мы свяжемся с вами в течение 1 рабочего дня."
            ),
            "aggression": (
                "Передаю вас специалисту для решения вопроса."
            ),
            "human_handoff": (
                "Соединяю с менеджером. "
                "Если сейчас вне рабочего времени — свяжемся утром."
            ),
        }

        return messages.get(
            intent.name, "Передаю ваш запрос специалисту для решения."
        )
