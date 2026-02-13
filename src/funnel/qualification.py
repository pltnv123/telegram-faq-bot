"""Этап квалификации (Qualification).

Цель: собрать минимум слотов для корректного оффера:
goal, context, deadline, budget_band, constraints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from beartype import beartype

from src.funnel.stages import BaseFunnelStage, FunnelStage, StageResult
from src.knowledge.faq_loader import KnowledgeBase
from src.nlu.slot_extractor import SlotCollection, SlotExtractor

if TYPE_CHECKING:
    from src.database.context import Message
    from src.nlu.intent_classifier import Intent


class QualificationStage(BaseFunnelStage):
    """Этап квалификации - сбор параметров."""

    stage_name = FunnelStage.QUALIFICATION

    @beartype
    def __init__(
        self, knowledge_base: KnowledgeBase, slot_extractor: SlotExtractor
    ) -> None:
        """Инициализация.

        Args:
            knowledge_base: База знаний
            slot_extractor: Экстрактор слотов
        """
        self.knowledge_base = knowledge_base
        self.slot_extractor = slot_extractor

    @beartype
    def get_required_slots(self) -> list[str]:
        """Обязательные слоты для квалификации."""
        return ["goal", "budget_band", "deadline"]

    @beartype
    def get_exit_criteria(self) -> dict[str, str]:
        """Критерий выхода: собраны goal, budget, deadline."""
        return {
            "criterion": "slots_collected",
            "description": "Понятно что, когда, примерно за сколько",
        }

    @beartype
    async def process(
        self,
        user_message: str,
        intent: Intent,
        slots: SlotCollection,
        conversation_history: list[Message],
    ) -> StageResult:
        """Обработать сообщение на этапе квалификации."""
        # Извлечь слоты из текущего сообщения
        new_slots = self.slot_extractor.extract(
            user_message, conversation_history, self.get_required_slots()
        )

        # Обновить существующие слоты
        for slot_name, slot_value in new_slots.slots.items():
            if slot_value.value:
                slots.set_value(slot_name, slot_value.value, slot_value.confidence)

        # Проверить завершён ли этап
        if self.is_complete(slots):
            # Квалификация завершена - переходим к офферу
            summary = self._create_summary(slots)
            return StageResult(
                stage=self.stage_name,
                success=True,
                response_text=summary,
                next_stage=FunnelStage.OFFER,
                collected_slots={
                    name: slots.get_value(name) or ""
                    for name in self.get_required_slots()
                },
            )

        # Запросить недостающие слоты
        question = self.slot_extractor.ask_next_missing(slots)
        return StageResult(
            stage=self.stage_name,
            success=False,  # Не завершён
            response_text=question,
            next_stage=FunnelStage.QUALIFICATION,  # Остаёмся
        )

    @beartype
    def _create_summary(self, slots: SlotCollection) -> str:
        """Создать резюме собранных параметров."""
        goal = slots.get_value("goal") or "не указано"
        budget = slots.get_value("budget_band") or "не указано"
        deadline = slots.get_value("deadline") or "не указано"

        return (
            f"Понял:\n"
            f"• Задача: {goal}\n"
            f"• Бюджет: {budget}\n"
            f"• Срок: {deadline}\n\n"
            f"Сейчас подберу варианты..."
        )

    @beartype
    def suggest_next_action(self, slots: SlotCollection) -> str:
        """CTA для квалификации."""
        missing = slots.get_missing_slots()
        if missing:
            return f"Уточните ещё {len(missing)} деталь(и) для точного предложения."
        return "Формирую варианты решения..."
