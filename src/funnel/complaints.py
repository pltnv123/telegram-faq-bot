"""Этап возвратов и претензий (Complaints).

Цель: принять обращение без спора, собрать доказательства, запустить процесс.
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


class ComplaintsStage(BaseFunnelStage):
    """Этап претензий - обработка жалоб и возвратов."""

    stage_name = FunnelStage.COMPLAINTS

    @beartype
    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        """Инициализация."""
        self.knowledge_base = knowledge_base

    @beartype
    def get_required_slots(self) -> list[str]:
        """Обязательные слоты для претензии."""
        return ["order_id", "contact"]

    @beartype
    async def process(
        self,
        user_message: str,
        intent: Intent,
        slots: SlotCollection,
        conversation_history: list[Message],
    ) -> StageResult:
        """Обработать претензию."""
        # Всегда требуется handoff для претензий
        response = (
            "Понял. Помогу оформить возврат/жалобу.\n\n"
            "Уточните:\n"
            "• Номер заказа\n"
            "• Причина (не подошло/дефект/ошибка/другое)\n"
            "• Контакт для связи\n\n"
            "Ответ по решению — до 7 рабочих дней."
        )

        return StageResult(
            stage=self.stage_name,
            success=True,
            response_text=response,
            next_stage=None,
            requires_handoff=True,
            handoff_reason="Возврат/претензия требует участия менеджера",
        )
