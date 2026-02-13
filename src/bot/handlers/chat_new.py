"""Обновлённый обработчик чата с интеграцией воронки по универсальному стандарту.

Интегрирует:
- NLU (Intent Classifier + Slot Extractor)
- Воронку (7 этапов)
- Handoff систему (тикеты)
- Метрики (event logging)
- Compliance (data minimization)
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message
from beartype import beartype

from src.ai.ollama_client import OllamaClient
from src.ai.prompts import create_stage_specific_prompt
from src.database.context import ConversationContext
from src.funnel.router import FunnelRouter
from src.funnel.stages import FunnelContext, FunnelStage
from src.handoff.escalation_rules import EscalationRules
from src.handoff.ticket_manager import TicketManager
from src.knowledge.faq_loader import KnowledgeBase
from src.knowledge.search import quick_faq_check
from src.metrics.event_logger import EventLogger
from src.nlu.intent_classifier import IntentClassifier
from src.nlu.slot_extractor import SlotCollection, SlotExtractor
from src.utils.loading_indicator import LoadingIndicator
from src.database.context import Message as ContextMessage

router = Router()

# Глобальное хранилище контекстов воронки (в production - в БД)
_funnel_contexts: dict[int, FunnelContext] = {}


@router.message(F.text)
@beartype
async def handle_text_message(
    message: Message,
    knowledge_base: KnowledgeBase,
    context: ConversationContext,
    ollama_client: OllamaClient,
) -> None:
    """Обработать текстовое сообщение с полной интеграцией стандарта.

    Args:
        message: Сообщение от пользователя
        knowledge_base: База знаний
        context: Менеджер контекста диалогов
        ollama_client: Клиент Ollama для AI
    """
    if not message.from_user or not message.text:
        return

    user_id = message.from_user.id
    user_question = message.text
    start_time = datetime.now()

    # Инициализировать зависимости
    intent_classifier = IntentClassifier()
    slot_extractor = SlotExtractor()
    funnel_router = FunnelRouter(knowledge_base, slot_extractor)
    event_logger = EventLogger(context.db_path)
    ticket_manager = TicketManager(context.db_path)

    # Записать событие начала диалога
    await event_logger.log_conversation_started(user_id)

    # Сохранить сообщение пользователя
    await context.save_message(user_id=user_id, role="user", content=user_question)

    # Загрузить историю диалога
    conversation_history = await context.get_context(user_id, limit=10)

    # ===== ШАГ 1: Классификация интента (NLU) =====
    intent = intent_classifier.classify(user_question, conversation_history)
    await event_logger.log_intent_classified(user_id, intent.name, intent.confidence)

    # ===== ШАГ 2: Проверка на необходимость handoff =====
    should_escalate, escalation_reason = EscalationRules.should_escalate(
        intent, intent.confidence
    )

    if should_escalate:
        # Немедленная эскалация для супер-приоритетных интентов
        await handle_escalation(
            message,
            user_id,
            intent,
            escalation_reason,
            ticket_manager,
            slot_extractor,
            conversation_history,
            event_logger,
        )
        return

    # ===== ШАГ 3: Quick FAQ check (быстрый путь) =====
    quick_result = quick_faq_check(user_question, knowledge_base, min_score=0.7)

    if quick_result:
        faq_item, score = quick_result
        ai_response = faq_item.answer
        print(f"Quick FAQ match (score: {score:.2f}), skipping funnel")

        # Сохранить и отправить
        await context.save_message(user_id=user_id, role="assistant", content=ai_response)
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        await event_logger.log_first_bot_response(user_id, elapsed_ms)
        await message.answer(ai_response, parse_mode=None)
        return

    # ===== ШАГ 4: Извлечение слотов =====
    # Получить или создать контекст воронки
    if user_id not in _funnel_contexts:
        slots = SlotCollection()
        _funnel_contexts[user_id] = FunnelContext(
            user_id=user_id, current_stage=FunnelStage.ACQUISITION, slots=slots
        )

    funnel_context = _funnel_contexts[user_id]

    # Извлечь слоты из текущего сообщения
    extracted_slots = slot_extractor.extract(user_question, conversation_history)
    for slot_name, slot_value in extracted_slots.slots.items():
        if slot_value.value:
            funnel_context.slots.set_value(
                slot_name, slot_value.value, slot_value.confidence
            )

    # ===== ШАГ 5: Маршрутизация через воронку =====
    old_stage = funnel_context.current_stage
    stage_result = await funnel_router.route(
        funnel_context, user_question, intent, conversation_history
    )

    # Записать изменение этапа если оно произошло
    if funnel_context.current_stage != old_stage:
        await event_logger.log_funnel_stage_changed(
            user_id, old_stage.value, funnel_context.current_stage.value
        )

    # Если этап требует handoff - создать тикет
    if stage_result.requires_handoff:
        await handle_stage_handoff(
            message,
            user_id,
            stage_result,
            ticket_manager,
            funnel_context.slots,
            conversation_history,
            event_logger,
        )
        return

    # ===== ШАГ 6: Генерация ответа =====
    ai_response = stage_result.response_text

    # Если ответ пустой или нужна AI генерация - запросить Ollama
    if not ai_response or len(ai_response) < 20:
        ai_response = await generate_ai_response(
            message,
            funnel_context,
            user_question,
            knowledge_base,
            conversation_history,
            ollama_client,
        )

    # ===== ШАГ 7: Сохранить и отправить ответ =====
    await context.save_message(user_id=user_id, role="assistant", content=ai_response)

    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
    await event_logger.log_first_bot_response(user_id, elapsed_ms)

    await message.answer(ai_response, parse_mode=None)


@beartype
async def handle_escalation(
    message: Message,
    user_id: int,
    intent,
    reason: str,
    ticket_manager: TicketManager,
    slot_extractor: SlotExtractor,
    conversation_history: list,
    event_logger: EventLogger,
) -> None:
    """Обработать эскалацию к менеджеру."""
    from src.handoff.ticket_manager import TicketType

    # Определить тип тикета
    ticket_type_map = {
        "privacy": TicketType.PRIVACY,
        "refund_request": TicketType.REFUND,
        "complaint": TicketType.COMPLAINT,
        "legal": TicketType.LEGAL,
    }
    ticket_type = ticket_type_map.get(intent.group, TicketType.SALES_LEAD)

    # Создать тикет
    slots = SlotCollection()
    contact = f"telegram_id_{user_id}"

    ticket = await ticket_manager.create_ticket(
        ticket_type=ticket_type,
        user_id=user_id,
        customer_contact=contact,
        summary=f"Эскалация: {intent.name} - {reason}",
        slots=slots,
        conversation_history=conversation_history,
        requested_action=intent.name,
    )

    await event_logger.log_ticket_created(
        user_id, ticket.ticket_id or 0, ticket_type.value, ticket.priority.value
    )

    # Сообщение пользователю
    escalation_message = EscalationRules.get_escalation_message(intent)
    await message.answer(escalation_message, parse_mode=None)


@beartype
async def handle_stage_handoff(
    message: Message,
    user_id: int,
    stage_result,
    ticket_manager: TicketManager,
    slots: SlotCollection,
    conversation_history: list,
    event_logger: EventLogger,
) -> None:
    """Обработать handoff из этапа воронки."""
    from src.handoff.ticket_manager import TicketType

    # Создать тикет
    ticket = await ticket_manager.create_ticket(
        ticket_type=TicketType.SALES_LEAD,
        user_id=user_id,
        customer_contact=f"telegram_id_{user_id}",
        summary=stage_result.handoff_reason or "Требуется участие менеджера",
        slots=slots,
        conversation_history=conversation_history,
    )

    await event_logger.log_ticket_created(
        user_id, ticket.ticket_id or 0, ticket.ticket_type.value, ticket.priority.value
    )

    # Отправить ответ с уведомлением о handoff
    response = stage_result.response_text or "Передаю ваш запрос специалисту."
    await message.answer(response, parse_mode=None)


@beartype
async def generate_ai_response(
    message: Message,
    funnel_context: FunnelContext,
    user_question: str,
    knowledge_base: KnowledgeBase,
    conversation_history: list,
    ollama_client: OllamaClient,
) -> str:
    """Генерировать AI ответ с использованием stage-specific промпта."""
    loading = None

    try:
        # Проверить доступность Ollama
        is_available = await ollama_client.check_health()

        if not is_available:
            return "Извините, AI временно недоступен. Свяжитесь с менеджером."

        # Запустить индикатор загрузки
        loading = await LoadingIndicator.start(message)

        # Создать stage-specific промпт
        slots_dict = {
            name: funnel_context.slots.get_value(name)
            for name in funnel_context.slots.slots.keys()
        }

        prompt = create_stage_specific_prompt(
            stage=funnel_context.current_stage.value,
            knowledge_base=knowledge_base,
            slots=slots_dict,
            conversation_history=conversation_history,
            user_question=user_question,
        )

        # Генерировать ответ через Ollama
        ai_response = await asyncio.wait_for(
            ollama_client.generate(prompt), timeout=90.0
        )

        return ai_response

    except asyncio.TimeoutError:
        if loading:
            await loading.update_phase("timeout")
        return "Извините, генерация заняла слишком много времени. Попробуйте ещё раз."

    finally:
        if loading:
            await loading.stop()
