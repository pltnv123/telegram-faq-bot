"""Главная точка входа приложения."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from beartype import beartype

from src.ai.ollama_client import OllamaClient
from src.bot.handlers import chat, menu, privacy, start  # Вернули старый рабочий chat handler
from src.config import get_config
from src.database.context import ConversationContext
from src.database.models import check_database_health, init_database
from src.knowledge.faq_loader import FAQLoader

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


@beartype
async def main() -> None:
    """Главная функция запуска бота."""
    logger.info("Starting Telegram FAQ Bot...")

    # Загрузить конфигурацию
    try:
        config = get_config()
        logger.info("[OK] Configuration loaded")
    except ValueError as e:
        logger.error(f"[ERROR] Configuration error: {e}")
        sys.exit(1)

    # Инициализировать базу данных
    try:
        await init_database(config.db_path)
        db_healthy = await check_database_health(config.db_path)
        if db_healthy:
            logger.info("[OK] Database initialized")
        else:
            logger.warning("[WARNING] Database issue, but continuing")
    except Exception as e:
        logger.error(f"[ERROR] Database initialization failed: {e}")
        sys.exit(1)

    # Загрузить базу знаний FAQ
    try:
        faq_path = Path("data/faq.json")
        faq_loader = FAQLoader(faq_path)
        knowledge_base = await faq_loader.load()
        logger.info(f"[OK] Loaded FAQ items: {len(knowledge_base.faq)}")
        logger.info(f"[OK] Loaded services: {len(knowledge_base.services)}")
    except Exception as e:
        logger.error(f"[ERROR] Failed to load FAQ: {e}")
        sys.exit(1)

    # Инициализировать Ollama клиент
    ollama_client = OllamaClient(
        api_url=config.ollama_api_url,
        model=config.ollama_model,
        temperature=config.ai_temperature,
        max_tokens=config.ai_max_tokens,
    )

    # Проверить доступность Ollama
    ollama_available = await ollama_client.check_health()
    if ollama_available:
        logger.info(f"[OK] Ollama is available (model: {config.ollama_model})")
    else:
        logger.warning(
            "[WARNING] Ollama is not available. Bot will work in fallback mode "
            "(simple FAQ search without AI)"
        )

    # Создать менеджер контекста диалогов
    context_manager = ConversationContext(config.db_path)

    # Инициализировать бота и диспетчер
    bot = Bot(
        token=config.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher()

    # Middleware для передачи зависимостей в handlers
    @dp.message.middleware()
    @beartype
    async def inject_dependencies(handler, event, data):  # type: ignore
        """Middleware для внедрения зависимостей."""
        data["knowledge_base"] = knowledge_base
        data["context"] = context_manager
        data["ollama_client"] = ollama_client
        return await handler(event, data)

    @dp.callback_query.middleware()
    @beartype
    async def inject_dependencies_callback(handler, event, data):  # type: ignore
        """Middleware для внедрения зависимостей в callback."""
        data["knowledge_base"] = knowledge_base
        data["context"] = context_manager
        data["ollama_client"] = ollama_client
        return await handler(event, data)

    # Зарегистрировать handlers (порядок важен!)
    dp.include_router(start.router)  # Команды /start, /help, /reset
    dp.include_router(privacy.router)  # Команда /privacy
    dp.include_router(menu.router)  # Обработка кнопок меню
    dp.include_router(chat.router)  # Обработка текстовых сообщений

    logger.info("[OK] Handlers registered")

    # Периодическая очистка старых сообщений
    async def cleanup_task() -> None:
        """Фоновая задача для очистки старых данных."""
        while True:
            try:
                await asyncio.sleep(3600)  # Раз в час
                deleted = await context_manager.cleanup_old_messages(
                    days=config.context_retention_days
                )
                if deleted > 0:
                    logger.info(f"[CLEANUP] Deleted old messages: {deleted}")
            except Exception as e:
                logger.error(f"Error in cleanup_task: {e}")

    # Запустить фоновую задачу очистки
    cleanup_task_obj = asyncio.create_task(cleanup_task())

    try:
        logger.info("[OK] Bot started and ready to receive messages!")
        logger.info(f"[INFO] Logs are saved to: {config.log_file}")
        logger.info("Press Ctrl+C to stop\n")

        # Запустить polling
        await dp.start_polling(bot)

    except KeyboardInterrupt:
        logger.info("\n[STOP] Received stop signal...")
    finally:
        # Graceful shutdown
        cleanup_task_obj.cancel()
        await ollama_client.close()
        await bot.session.close()
        logger.info("[STOP] Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
