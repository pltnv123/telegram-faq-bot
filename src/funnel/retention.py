"""Этап повторных продаж (Retention).

Цель: релевантный upsell/cross-sell после успешного решения.
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


class RetentionStage(BaseFunnelStage):
    """Этап повторных продаж."""

    stage_name = FunnelStage.RETENTION

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
        """Обработать возможность upsell."""
        # Предлагаем дополнительные услуги только если основной вопрос решён
        response = (
            "Рад что получилось! "
            "Если понадобится что-то ещё — обращайтесь."
        )

        return StageResult(
            stage=self.stage_name,
            success=True,
            response_text=response,
            next_stage=None,
        )
