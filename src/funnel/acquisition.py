"""Этап привлечения (Acquisition).

Цель: быстро классифицировать обращение в одно из направлений:
узнать, купить, получить поддержку, пожаловаться/вернуть, юридическое/данные.
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


class AcquisitionStage(BaseFunnelStage):
    """Этап привлечения - первый контакт с клиентом."""

    stage_name = FunnelStage.ACQUISITION

    @beartype
    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        """Инициализация этапа.

        Args:
            knowledge_base: База знаний компании
        """
        self.knowledge_base = knowledge_base

    @beartype
    def get_required_slots(self) -> list[str]:
        """На этапе привлечения собираем только channel/context."""
        return []  # Нет обязательных слотов

    @beartype
    def get_exit_criteria(self) -> dict[str, str]:
        """Критерий выхода: пользователь выбрал направление."""
        return {
            "criterion": "direction_chosen",
            "description": "Пользователь описал задачу или выбрал направление",
        }

    @beartype
    async def process(
        self,
        user_message: str,
        intent: Intent,
        slots: SlotCollection,
        conversation_history: list[Message],
    ) -> StageResult:
        """Обработать сообщение на этапе привлечения.

        Args:
            user_message: Сообщение пользователя
            intent: Классифицированный интент
            slots: Собранные слоты
            conversation_history: История диалога

        Returns:
            StageResult: Результат обработки
        """
        user_message_lower = user_message.lower()

        # Сценарий A: Приветствие/смолток
        if self._is_greeting_or_smalltalk(user_message_lower):
            response = self._handle_greeting()
            return StageResult(
                stage=self.stage_name,
                success=True,
                response_text=response,
                next_stage=FunnelStage.ACQUISITION,  # Остаёмся на том же этапе
            )

        # Сценарий B: "Гуляет" - не знает что хочет
        if self._is_browsing(user_message_lower):
            response = self._handle_browsing()
            return StageResult(
                stage=self.stage_name,
                success=True,
                response_text=response,
                next_stage=FunnelStage.QUALIFICATION,
            )

        # Если есть конкретный интент - переходим к квалификации
        if intent.name != "general" and intent.name != "greet":
            # Направление определено
            return StageResult(
                stage=self.stage_name,
                success=True,
                response_text="",  # Ответ сформируется на следующем этапе
                next_stage=FunnelStage.QUALIFICATION,
                metadata={"intent": intent.name},
            )

        # Дефолт: помогаем выбрать направление
        response = self._handle_general_inquiry()
        return StageResult(
            stage=self.stage_name,
            success=True,
            response_text=response,
            next_stage=FunnelStage.ACQUISITION,
        )

    @beartype
    def _is_greeting_or_smalltalk(self, text_lower: str) -> bool:
        """Проверить является ли сообщение приветствием или small talk."""
        greetings = [
            "привет",
            "здравствуй",
            "добрый",
            "как дела",
            "как ты",
            "что нового",
        ]
        return any(greeting in text_lower for greeting in greetings)

    @beartype
    def _is_browsing(self, text_lower: str) -> bool:
        """Проверить "гуляет" ли пользователь (не знает что хочет)."""
        browsing_keywords = [
            "что вы делаете",
            "чем занимаетесь",
            "что предлагаете",
            "покажите",
            "расскажите",
            "что у вас",
        ]
        return any(keyword in text_lower for keyword in browsing_keywords)

    @beartype
    def _handle_greeting(self) -> str:
        """Ответ на приветствие."""
        company_name = self.knowledge_base.company.name
        return (
            f"Привет! На связи помощник {company_name} 🙂 "
            f"Чем помочь: услуги/цены/сроки/контакты/поддержка?"
        )

    @beartype
    def _handle_browsing(self) -> str:
        """Ответ когда пользователь "гуляет"."""
        # Формируем краткий список направлений
        services = self.knowledge_base.services
        if len(services) >= 2:
            service_names = [s.name for s in services[:3]]
            services_list = ", ".join(service_names)
            return (
                f"Мы помогаем с: {services_list}.\n\n"
                f"Что ближе к вашей задаче? Или нужна рекомендация?"
            )
        else:
            return self._handle_general_inquiry()

    @beartype
    def _handle_general_inquiry(self) -> str:
        """Ответ на общий запрос."""
        return (
            "Чем могу помочь?\n"
            "• Узнать об услугах и ценах\n"
            "• Оформить заказ\n"
            "• Поддержка по существующему заказу\n"
            "• Возврат или жалоба"
        )

    @beartype
    def suggest_next_action(self, slots: SlotCollection) -> str:
        """CTA для этапа привлечения."""
        return "Выберите что вас интересует, и я помогу дальше."
