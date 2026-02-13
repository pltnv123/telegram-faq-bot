"""Этап сопровождения (Support).

Цель: закрывать типовые вопросы self-service (статусы, how-to).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from beartype import beartype

from src.funnel.stages import BaseFunnelStage, FunnelStage, StageResult
from src.knowledge.faq_loader import KnowledgeBase
from src.nlu.slot_extractor import SlotCollection

if TYPE_CHECKING:
    from src.database.context import Message
    from src.nlu.intent_classifier import Intent


class SupportStage(BaseFunnelStage):
    """Этап поддержки."""

    stage_name = FunnelStage.SUPPORT

    @beartype
    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        """Инициализация."""
        self.knowledge_base = knowledge_base

    @beartype
    async def process(
        self,
        user_message: str,
        intent: Intent,
        slots: SlotCollection,
        conversation_history: list[Message],
    ) -> StageResult:
        """Обработать запрос поддержки."""
        # Простая логика: если есть order_id - проверяем статус
        order_id = slots.get_value("order_id")

        if order_id:
            response = f"Проверяю заказ №{order_id}. Свяжитесь с поддержкой для актуального статуса."
        else:
            response = "Напишите номер заказа для проверки статуса."

        return StageResult(
            stage=self.stage_name,
            success=True,
            response_text=response,
            next_stage=None,
        )
