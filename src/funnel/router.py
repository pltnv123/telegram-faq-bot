"""Router для управления переходами между этапами воронки."""

from __future__ import annotations

from typing import TYPE_CHECKING

from beartype import beartype

from src.funnel.acquisition import AcquisitionStage
from src.funnel.closing import ClosingStage
from src.funnel.complaints import ComplaintsStage
from src.funnel.offer import OfferStage
from src.funnel.qualification import QualificationStage
from src.funnel.retention import RetentionStage
from src.funnel.stages import FunnelContext, FunnelStage, StageResult
from src.funnel.support import SupportStage
from src.knowledge.faq_loader import KnowledgeBase
from src.nlu.slot_extractor import SlotExtractor

if TYPE_CHECKING:
    from src.database.context import Message
    from src.nlu.intent_classifier import Intent


class FunnelRouter:
    """Маршрутизатор между этапами воронки."""

    @beartype
    def __init__(
        self, knowledge_base: KnowledgeBase, slot_extractor: SlotExtractor
    ) -> None:
        """Инициализация router.

        Args:
            knowledge_base: База знаний
            slot_extractor: Экстрактор слотов
        """
        self.knowledge_base = knowledge_base
        self.slot_extractor = slot_extractor

        # Создаём все этапы
        self.stages = {
            FunnelStage.ACQUISITION: AcquisitionStage(knowledge_base),
            FunnelStage.QUALIFICATION: QualificationStage(
                knowledge_base, slot_extractor
            ),
            FunnelStage.OFFER: OfferStage(knowledge_base),
            FunnelStage.CLOSING: ClosingStage(knowledge_base, slot_extractor),
            FunnelStage.SUPPORT: SupportStage(knowledge_base),
            FunnelStage.COMPLAINTS: ComplaintsStage(knowledge_base),
            FunnelStage.RETENTION: RetentionStage(knowledge_base),
        }

    @beartype
    async def route(
        self,
        funnel_context: FunnelContext,
        user_message: str,
        intent: Intent,
        conversation_history: list[Message],
    ) -> StageResult:
        """Маршрутизировать сообщение на соответствующий этап.

        Args:
            funnel_context: Контекст воронки пользователя
            user_message: Сообщение пользователя
            intent: Классифицированный интент
            conversation_history: История диалога

        Returns:
            StageResult: Результат обработки этапа
        """
        # Определить текущий этап
        current_stage = self._determine_stage_by_intent(intent, funnel_context)

        # Обновить контекст если этап изменился
        if current_stage != funnel_context.current_stage:
            funnel_context.move_to_stage(current_stage)

        # Получить обработчик этапа
        stage_handler = self.stages.get(current_stage)
        if not stage_handler:
            # Fallback на acquisition
            stage_handler = self.stages[FunnelStage.ACQUISITION]

        # Обработать сообщение на текущем этапе
        result = await stage_handler.process(
            user_message, intent, funnel_context.slots, conversation_history
        )

        # Если есть переход на следующий этап - обновить контекст
        if result.next_stage and result.next_stage != current_stage:
            funnel_context.move_to_stage(result.next_stage)

        return result

    @beartype
    def _determine_stage_by_intent(
        self, intent: Intent, funnel_context: FunnelContext
    ) -> FunnelStage:
        """Определить этап по интенту пользователя.

        Args:
            intent: Интент
            funnel_context: Контекст воронки

        Returns:
            FunnelStage: Этап воронки
        """
        # Супер-приоритетные интенты всегда переопределяют текущий этап

        # Претензии
        if intent.group == "complaints":
            return FunnelStage.COMPLAINTS

        # Privacy/данные обрабатываются через handoff, но формально это support
        if intent.group == "privacy":
            return FunnelStage.SUPPORT  # Будет handoff

        # Поддержка
        if intent.group == "support":
            return FunnelStage.SUPPORT

        # Транзакции
        if intent.group == "transactions":
            # Если уже есть слоты - переходим к closing
            if funnel_context.slots.get_value("goal"):
                return FunnelStage.CLOSING
            else:
                return FunnelStage.QUALIFICATION

        # Предпродажа
        if intent.group == "presales":
            # Если нет слотов - квалификация
            if not funnel_context.slots.get_value("goal"):
                return FunnelStage.QUALIFICATION
            else:
                # Уже есть данные - оффер
                return FunnelStage.OFFER

        # По умолчанию - текущий этап или acquisition
        if funnel_context.current_stage:
            return funnel_context.current_stage

        return FunnelStage.ACQUISITION
