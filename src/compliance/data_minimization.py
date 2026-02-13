"""Логика минимизации сбора PII.

Реализует принципы data minimization и purpose limitation (GDPR Art. 5).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from beartype import beartype

if TYPE_CHECKING:
    from src.funnel.stages import FunnelStage


class DataMinimization:
    """Правила минимизации сбора персональных данных."""

    # Какие данные можно собирать на каждом этапе
    ALLOWED_PII_BY_STAGE = {
        "acquisition": [],  # Никаких PII
        "qualification": [],  # Только бизнес-параметры (budget, deadline)
        "offer": [],  # Всё ещё без PII
        "closing": ["contact"],  # Только при создании заявки
        "support": ["order_id"],  # order_id вместо PII
        "complaints": ["order_id", "contact"],  # Для обработки претензии
        "retention": [],  # Без PII для upsell
    }

    @beartype
    @staticmethod
    def is_pii_allowed(stage: FunnelStage, pii_type: str) -> bool:
        """Проверить разрешён ли сбор PII на данном этапе.

        Args:
            stage: Этап воронки
            pii_type: Тип PII (contact, email, phone, etc.)

        Returns:
            bool: Разрешён ли сбор
        """
        stage_name = stage.value if hasattr(stage, "value") else str(stage)
        allowed = DataMinimization.ALLOWED_PII_BY_STAGE.get(stage_name, [])
        return pii_type in allowed

    @beartype
    @staticmethod
    def get_minimal_request_text(stage: FunnelStage) -> str:
        """Получить минималистичный запрос PII.

        Args:
            stage: Этап

        Returns:
            str: Текст запроса
        """
        stage_name = stage.value if hasattr(stage, "value") else str(stage)

        if stage_name == "closing":
            return "Для оформления нужен контакт (телефон или email)."

        if stage_name == "complaints":
            return "Для обработки жалобы укажите номер заказа и контакт."

        return ""

    @beartype
    @staticmethod
    def should_use_order_id_instead(context: dict) -> bool:
        """Проверить можно ли использовать order_id вместо PII.

        Args:
            context: Контекст диалога

        Returns:
            bool: True если можно использовать order_id
        """
        # Если есть order_id в контексте - используем его вместо запроса PII
        return "order_id" in context and context["order_id"]

    @beartype
    @staticmethod
    def get_retention_days_by_purpose(purpose: str) -> int:
        """Получить срок хранения данных по цели обработки.

        Args:
            purpose: Цель обработки

        Returns:
            int: Срок хранения в днях
        """
        retention_map = {
            "conversation_context": 7,  # История диалога - 7 дней
            "order_processing": 365,  # Обработка заказов - 1 год
            "complaint_handling": 1095,  # Претензии - 3 года (по закону)
            "analytics": 30,  # Аналитика - 30 дней
        }

        return retention_map.get(purpose, 7)  # По умолчанию 7 дней
