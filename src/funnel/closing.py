"""Этап закрытия (Closing).

Цель: довести до транзакции или созвона - собрать контакт,
оформить заказ/счёт/бронь, подтвердить условия.
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


class ClosingStage(BaseFunnelStage):
    """Этап закрытия - создание заявки/заказа."""

    stage_name = FunnelStage.CLOSING

    @beartype
    def __init__(
        self, knowledge_base: KnowledgeBase, slot_extractor: SlotExtractor
    ) -> None:
        """Инициализация."""
        self.knowledge_base = knowledge_base
        self.slot_extractor = slot_extractor

    @beartype
    def get_required_slots(self) -> list[str]:
        """Обязательные слоты для закрытия."""
        return ["contact"]

    @beartype
    def get_exit_criteria(self) -> dict[str, str]:
        """Критерий выхода: сформирован заказ/счет/бронь."""
        return {
            "criterion": "order_created",
            "description": "Сформирован заказ/счет/бронь/заявка",
        }

    @beartype
    async def process(
        self,
        user_message: str,
        intent: Intent,
        slots: SlotCollection,
        conversation_history: list[Message],
    ) -> StageResult:
        """Обработать сообщение на этапе закрытия."""
        # Извлечь контакт
        new_slots = self.slot_extractor.extract(user_message, conversation_history)
        if "contact" in new_slots.slots and new_slots.slots["contact"].value:
            contact = new_slots.slots["contact"].value
            slots.set_value("contact", contact)

        # Если контакт есть - создаём заявку
        if slots.get_value("contact"):
            response = self._create_order_confirmation(slots)
            return StageResult(
                stage=self.stage_name,
                success=True,
                response_text=response,
                next_stage=None,  # Воронка завершена
                metadata={"order_created": "true"},
            )

        # Запросить контакт
        return StageResult(
            stage=self.stage_name,
            success=False,
            response_text="Оставьте контакт для связи (телефон или email).",
            next_stage=FunnelStage.CLOSING,
        )

    @beartype
    def _create_order_confirmation(self, slots: SlotCollection) -> str:
        """Создать подтверждение заказа."""
        contact = slots.get_value("contact") or ""
        goal = slots.get_value("goal") or "услуга"
        budget = slots.get_value("budget_band") or "уточнение"
        deadline = slots.get_value("deadline") or "уточнение"

        phone = self.knowledge_base.company.phone
        email = self.knowledge_base.company.email

        return (
            f"✅ Заявка принята!\n\n"
            f"Ваши данные:\n"
            f"• Задача: {goal}\n"
            f"• Бюджет: {budget}\n"
            f"• Срок: {deadline}\n"
            f"• Контакт: {contact}\n\n"
            f"Менеджер свяжется с вами в течение часа.\n"
            f"Если срочно: {phone}"
        )

    @beartype
    def suggest_next_action(self, slots: SlotCollection) -> str:
        """CTA для закрытия."""
        return "Оставьте контакт для завершения оформления."
