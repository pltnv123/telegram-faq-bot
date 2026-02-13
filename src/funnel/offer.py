"""Этап оффера (Offer).

Цель: превратить квалификацию в конкретный следующий шаг:
предложение пакета, сравнение вариантов, назначение звонка, выдача ссылки на оплату.
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


class OfferStage(BaseFunnelStage):
    """Этап оффера - формирование предложения."""

    stage_name = FunnelStage.OFFER

    @beartype
    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        """Инициализация."""
        self.knowledge_base = knowledge_base

    @beartype
    def get_required_slots(self) -> list[str]:
        """На этапе оффера нужно подтверждение выбора."""
        return []

    @beartype
    def get_exit_criteria(self) -> dict[str, str]:
        """Критерий выхода: пользователь согласен на действие."""
        return {
            "criterion": "offer_accepted",
            "description": "Пользователь согласен на заказ/звонок/ссылку/оплату",
        }

    @beartype
    async def process(
        self,
        user_message: str,
        intent: Intent,
        slots: SlotCollection,
        conversation_history: list[Message],
    ) -> StageResult:
        """Обработать сообщение на этапе оффера."""
        # Проверить хочет ли заказать
        if self._user_wants_to_order(user_message.lower()):
            return StageResult(
                stage=self.stage_name,
                success=True,
                response_text="Отлично! Оформляем заказ.",
                next_stage=FunnelStage.CLOSING,
            )

        # Сформировать оффер на основе собранных слотов
        offer_text = self._create_offer(slots)

        return StageResult(
            stage=self.stage_name,
            success=True,
            response_text=offer_text,
            next_stage=FunnelStage.OFFER,  # Ждём подтверждения
        )

    @beartype
    def _user_wants_to_order(self, text_lower: str) -> bool:
        """Проверить хочет ли пользователь заказать."""
        order_keywords = [
            "заказ",
            "оформ",
            "согласен",
            "подходит",
            "беру",
            "давайте",
            "да",
        ]
        return any(keyword in text_lower for keyword in order_keywords)

    @beartype
    def _create_offer(self, slots: SlotCollection) -> str:
        """Создать текст предложения."""
        services = self.knowledge_base.services

        if not services:
            return "Свяжитесь с менеджером для подбора решения."

        # Простой оффер: показать 2-3 варианта
        if len(services) >= 2:
            s1 = services[0]
            s2 = services[1]

            return (
                f"Вижу 2 подходящих варианта:\n\n"
                f"Вариант A — {s1.name}\n"
                f"• {s1.description}\n"
                f"• Цена: {s1.price}\n"
                f"• Срок: {s1.duration}\n\n"
                f"Вариант B — {s2.name}\n"
                f"• {s2.description}\n"
                f"• Цена: {s2.price}\n"
                f"• Срок: {s2.duration}\n\n"
                f"Какой ближе — A или B?"
            )
        else:
            # Один вариант
            s = services[0]
            return (
                f"Подходит: {s.name}\n"
                f"• {s.description}\n"
                f"• Цена: {s.price}\n"
                f"• Срок: {s.duration}\n\n"
                f"Оформляем?"
            )

    @beartype
    def suggest_next_action(self, slots: SlotCollection) -> str:
        """CTA для оффера."""
        return "Выберите вариант или уточните детали."
