"""Обработчик текстовых сообщений (основной диалог)."""

from __future__ import annotations

import asyncio
from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message
from beartype import beartype

from src.ai.ollama_client import OllamaClient
from src.ai.prompts import create_sales_chat_messages
from src.bot.keyboards import contextual_quick_replies
from src.database.context import ConversationContext
from src.knowledge.faq_loader import KnowledgeBase
from src.knowledge.search import format_faq_results, quick_faq_check, search_faq
from src.utils.intent_detection import detect_user_intent, should_show_hints
from src.utils.lead_scoring import calculate_lead_score, detect_funnel_stage
from src.utils.loading_indicator import LoadingIndicator
from src.utils.onboarding import get_onboarding_tip, should_show_onboarding_tip
from src.utils.text_filter import clean_text

router = Router()

# Кэш для отслеживания последней показанной подсказки
_last_tips_shown: dict[int, int] = {}


@router.message(F.text)
@beartype
async def handle_text_message(
    message: Message,
    knowledge_base: KnowledgeBase,
    context: ConversationContext,
    ollama_client: OllamaClient,
) -> None:
    """Обработать текстовое сообщение пользователя.

    Args:
        message: Сообщение от пользователя
        knowledge_base: База знаний
        context: Менеджер контекста диалогов
        ollama_client: Клиент Ollama для AI генерации
    """
    if not message.from_user or not message.text:
        return

    user_id = message.from_user.id
    user_question = message.text

    # Определить намерение пользователя
    intent = detect_user_intent(user_question)

    # Сохранить вопрос пользователя в БД
    await context.save_message(
        user_id=user_id,
        role="user",
        content=user_question,
    )

    # Загрузить историю диалога (последние 5 сообщений для лучшего контекста)
    conversation_history = await context.get_context(user_id, limit=5)

    # Оценить температуру лида и этап воронки
    lead_score = calculate_lead_score(
        user_message=user_question,
        conversation_history=conversation_history,
        intent=intent,
    )

    funnel_stage = detect_funnel_stage(
        conversation_history=conversation_history,
        lead_score=lead_score,
    )

    # Попытка 1: Быстрая проверка FAQ для простых вопросов (без AI)
    # Если найдено ОЧЕНЬ хорошее совпадение (score >= 0.75) - ответить мгновенно
    # Повышен порог чтобы не перебивать диалог
    quick_result = quick_faq_check(user_question, knowledge_base, min_score=0.75)
    
    ai_response = None
    if quick_result:
        # Найден точный FAQ ответ - отвечаем мгновенно без AI
        faq_item, score = quick_result
        ai_response = faq_item.answer
        try:
            print(f"Quick FAQ match found (score: {score:.2f}), skipping AI")
        except UnicodeEncodeError:
            print("Quick FAQ match found, skipping AI")
    
    # Попытка 2: Использовать Ollama AI с продающим промптом (только если нет быстрого ответа)
    loading = None
    status_msg = None  # Сообщение для streaming режима
    used_streaming = False  # Флаг успешного использования streaming
    
    if not ai_response:
        try:
            # Проверить доступность Ollama
            is_ollama_available = await ollama_client.check_health()

            if is_ollama_available:
                # Создать продающие сообщения для chat API
                chat_messages = create_sales_chat_messages(
                    knowledge_base=knowledge_base,
                    conversation_history=conversation_history,
                    user_question=user_question,
                    lead_score=lead_score,
                    funnel_stage=funnel_stage,
                )
                
                try:
                    # Попытка 1: Streaming генерация (real-time обновление)
                    
                    # Базовые фразы для анимации
                    BASE_PHRASES = [
                        "Думаю над ответом...",
                        "Анализирую вопрос...",
                        "Формирую ответ...",
                    ]
                    
                    # Вращающиеся эмодзи (циклически меняются)
                    SPINNERS = ["🔄", "⏳", "⌛"]
                    
                    # Функция генерации красивого прогресс-бара с фиолетовыми точками
                    def generate_progress_with_bar(phrase: str, spinner: str, progress: int) -> str:
                        """Генерация прогресс-бара с цветными точками.
                        
                        Args:
                            phrase: Текстовая фраза
                            spinner: Анимированный эмодзи
                            progress: Прогресс в процентах (0-100)
                            
                        Returns:
                            str: Прогресс с визуальным баром в две строки
                        """
                        width = 10
                        filled = int((progress / 100) * width)
                        empty = width - filled
                        # Фиолетовые заполненные точки и белые пустые
                        bar = "🟣" * filled + "⚪" * empty
                        return f"{spinner} {phrase}\n{bar} {progress}%"
                    
                    # Отправить начальное сообщение
                    status_msg = await message.answer(
                        generate_progress_with_bar(BASE_PHRASES[0], SPINNERS[0], 0)
                    )
                    start_time = datetime.now()
                    last_text_change = datetime.now()  # Для отдельного контроля смены текста
                    
                    # Накопитель для полного текста и throttling
                    full_response: list[str] = []
                    last_update = datetime.now()
                    current_phrase_index = 0
                    MIN_UPDATE_INTERVAL = 1.0  # Telegram API limit: 1 req/sec
                    SPINNER_INTERVAL = 0.4  # Смайлик крутится быстро
                    TEXT_CHANGE_INTERVAL = 3.0  # Текст меняется редко (комфортно глазу)
                    animation_stopped = False
                    
                    # Подсчет прогресса генерации
                    token_count = 0
                    estimated_max_tokens = 300  # Из AI_MAX_TOKENS в config
                    
                    # Фоновая анимация индикатора с минималистичным прогрессом
                    async def animate_thinking_indicator() -> None:
                        """Анимировать индикатор с минималистичным прогрессом."""
                        nonlocal token_count
                        spinner_index = 0
                        phrase_index = 0
                        last_text_change_time = datetime.now()
                        
                        try:
                            while not animation_stopped:
                                await asyncio.sleep(SPINNER_INTERVAL)  # Быстрое вращение смайлика
                                if not full_response and not animation_stopped:
                                    # Вращать смайлик КАЖДЫЙ цикл (быстро)
                                    spinner_index = (spinner_index + 1) % len(SPINNERS)
                                    
                                    # Менять текст РЕДКО (каждые TEXT_CHANGE_INTERVAL секунд)
                                    elapsed_since_text = (datetime.now() - last_text_change_time).total_seconds()
                                    if elapsed_since_text >= TEXT_CHANGE_INTERVAL:
                                        phrase_index = (phrase_index + 1) % len(BASE_PHRASES)
                                        last_text_change_time = datetime.now()
                                    
                                    # Рассчитать прогресс
                                    if token_count == 0:
                                        # Имитация до первого токена
                                        elapsed = (datetime.now() - start_time).total_seconds()
                                        fake_progress = min(95, int(elapsed * 5))  # ~5% в секунду
                                        progress_text = generate_progress_with_bar(
                                            BASE_PHRASES[phrase_index],
                                            SPINNERS[spinner_index],
                                            fake_progress
                                        )
                                    else:
                                        # Реальный прогресс после первого токена
                                        real_progress = min(99, int((token_count / estimated_max_tokens) * 100))
                                        progress_text = generate_progress_with_bar(
                                            "Генерирую...",
                                            SPINNERS[spinner_index],
                                            real_progress
                                        )
                                    
                                    try:
                                        await status_msg.edit_text(progress_text, parse_mode=None)
                                    except Exception:
                                        pass
                        except asyncio.CancelledError:
                            pass
                    
                    # Запустить анимацию в фоне
                    animation_task = asyncio.create_task(animate_thinking_indicator())
                    
                    async def on_token(token: str) -> None:
                        """Callback для сбора токенов без постепенного обновления."""
                        nonlocal animation_stopped, token_count
                        full_response.append(token)
                        token_count += 1
                        
                        # Если получили первый токен - остановить анимацию
                        if token_count == 1 and not animation_stopped:
                            animation_stopped = True
                    
                    # Запустить streaming генерацию
                    streaming_success = False
                    try:
                        ai_response = await ollama_client.chat_stream(
                            chat_messages,
                            on_token=on_token
                        )
                        
                        # КРИТИЧЕСКИ ВАЖНО: если streaming успешен, отмечаем это СРАЗУ
                        if ai_response and len(ai_response.strip()) > 0:
                            streaming_success = True
                        
                    except Exception as streaming_error:
                        # ВАЖНО: Если streaming успешен - НЕ запускать fallback
                        if streaming_success:
                            # Streaming завершился успешно, просто остановить анимацию
                            animation_stopped = True
                            animation_task.cancel()
                            try:
                                await animation_task
                            except asyncio.CancelledError:
                                pass
                        else:
                            # Streaming провалился - запустить fallback режим
                            # Остановить анимацию при ошибке
                            animation_stopped = True
                            animation_task.cancel()
                            try:
                                await animation_task
                            except asyncio.CancelledError:
                                pass
                            
                            # Попытка 2: Fallback на обычный режим без streaming
                            try:
                                print(f"Streaming failed: {streaming_error}, falling back to non-streaming mode")
                            except UnicodeEncodeError:
                                print("Streaming failed, falling back to non-streaming mode")
                            
                            # Показать индикатор загрузки для fallback режима
                            try:
                                await status_msg.edit_text("Думаю над ответом... 🧠")
                            except Exception:
                                pass
                            
                            loading = await LoadingIndicator.start(message)
                            try:
                                ai_response = await ollama_client.chat(chat_messages)
                                # POST-PROCESSING: Очистка для fallback режима
                                if ai_response:
                                    ai_response = clean_text(ai_response)
                            finally:
                                await loading.stop()
                                # Удалить status_msg т.к. LoadingIndicator уже удалил свое сообщение
                                try:
                                    await status_msg.delete()
                                except Exception:
                                    pass
                    
                    # ПОСТ-ОБРАБОТКА: Если streaming успешен, обработать ответ ВНЕ try блока
                    if streaming_success and ai_response:
                        # Очистка английских слов и грамматических ошибок
                        ai_response = clean_text(ai_response)
                        
                        # Остановить анимацию
                        animation_stopped = True
                        animation_task.cancel()
                        try:
                            await animation_task
                        except asyncio.CancelledError:
                            pass
                        
                        # Отметить успешное использование streaming
                        used_streaming = True
                    
                except asyncio.TimeoutError:
                    # Timeout - переключаемся на fallback поиск
                    print("Ollama timeout, switching to fallback")
                    try:
                        await status_msg.edit_text("Ответ занимает больше времени... 🔍")
                    except Exception:
                        pass

        except Exception as e:
            try:
                print(f"Ошибка при работе с Ollama: {e}")
            except UnicodeEncodeError:
                print("Ошибка при работе с Ollama")
            if loading:
                await loading.stop()
                loading = None
            # Удалить status_msg если был создан
            if status_msg:
                try:
                    await status_msg.delete()
                except Exception:
                    pass
                status_msg = None

    # Попытка 3: Fallback на простой поиск по FAQ
    if not ai_response:
        try:
            print("Ollama недоступна или не вернула ответ. Использую fallback поиск.")
        except UnicodeEncodeError:
            pass  # Игнорируем ошибку кодировки

        # Простой поиск по FAQ с пониженным порогом
        found_faq = search_faq(
            query=user_question,
            knowledge_base=knowledge_base,
            top_k=1,
            min_score=0.2,  # Понижен порог для fallback режима
        )

        if found_faq:
            ai_response = format_faq_results(found_faq)
        else:
            # Попытка 3: Умный fallback на основе общего намерения
            from src.utils.smart_fallback import (
                detect_general_intent,
                generate_fallback_response,
            )

            general_intent = detect_general_intent(user_question)

            if general_intent:
                ai_response = generate_fallback_response(
                    intent=general_intent,
                    knowledge_base=knowledge_base,
                    conversation_history=conversation_history,
                )

            # Если все еще нет ответа - предложить контакты
            if not ai_response:
                ai_response = knowledge_base.phrases.not_found.format(
                    phone=knowledge_base.company.phone,
                    email=knowledge_base.company.email,
                    telegram=knowledge_base.company.telegram,
                )

    # Если все еще нет ответа - показать ошибку
    if not ai_response:
        ai_response = knowledge_base.phrases.error

    # Добавить hints если нужно
    formatted_response = ai_response
    if should_show_hints(ai_response, intent):
        formatted_response += "\n\n━━━━━━━━━━━━━━━\n"
        formatted_response += "\n💡 Хотите узнать больше? Используйте /menu"

    # Сохранить ответ в БД
    await context.save_message(
        user_id=user_id,
        role="assistant",
        content=ai_response,
    )

    # Определить нужно ли показывать кнопки
    # Показываем только для конкретных намерений, не для general
    show_buttons = intent in ["pricing", "services", "contacts", "order"]
    
    # Получить контекстные quick replies кнопки (или удалить их)
    reply_markup = contextual_quick_replies(intent, show_buttons=show_buttons)

    # Отправить или обновить ответ пользователю
    if used_streaming and status_msg:
        # Если использовали streaming - обновить существующее сообщение
        try:
            await status_msg.edit_text(
                text=formatted_response,
                reply_markup=reply_markup,
                parse_mode=None,
            )
        except Exception as e:
            # Если не получилось отредактировать - отправить новое сообщение
            try:
                await status_msg.delete()
            except Exception:
                pass
            await message.answer(
                text=formatted_response,
                reply_markup=reply_markup,
                parse_mode=None,
            )
    else:
        # Обычный режим - отправить новое сообщение
        # Удалить status_msg если он есть (fallback режим)
        if status_msg:
            try:
                await status_msg.delete()
            except Exception:
                pass
        
        await message.answer(
            text=formatted_response,
            reply_markup=reply_markup,
            parse_mode=None,  # Отключаем парсинг Markdown/HTML
        )

    # Проверить нужно ли показать onboarding подсказку
    # NOTE: Онбординг подсказки отключены для более чистого UX
    # stats = await context.get_user_stats(user_id)
    # message_count = stats["total_messages"] // 2  # Делим на 2 т.к. сохраняем user+assistant

    # last_tip = _last_tips_shown.get(user_id)
    # if should_show_onboarding_tip(message_count, last_tip):
    #     tip = get_onboarding_tip(message_count)
    #     if tip:
    #         # Показать подсказку через небольшую паузу
    #         await asyncio.sleep(1)
    #         await message.answer(tip)
    #         _last_tips_shown[user_id] = message_count
