"""Конфигурация приложения из переменных окружения."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from beartype import beartype
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


@beartype
@dataclass(frozen=True)
class Config:
    """Конфигурация приложения."""

    # Telegram настройки
    telegram_bot_token: str

    # Ollama настройки
    ollama_api_url: str
    ollama_model: str

    # База данных
    db_path: Path

    # Контекст диалога
    max_context_messages: int
    context_retention_days: int

    # AI генерация
    ai_temperature: float
    ai_max_tokens: int

    # Логирование
    log_level: str
    log_file: str

    # Компания
    company_name: str

    @staticmethod
    def from_env() -> Config:
        """Создать конфигурацию из переменных окружения.

        Returns:
            Config: Объект конфигурации

        Raises:
            ValueError: Если обязательные переменные не установлены
        """
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN не установлен. "
                "Создайте .env файл на основе .env.example"
            )

        return Config(
            telegram_bot_token=telegram_token,
            ollama_api_url=os.getenv("OLLAMA_API_URL", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            db_path=Path(os.getenv("DB_PATH", "storage/conversations.db")),
            max_context_messages=int(os.getenv("MAX_CONTEXT_MESSAGES", "5")),  # Уменьшили с 10 до 5
            context_retention_days=int(os.getenv("CONTEXT_RETENTION_DAYS", "7")),
            ai_temperature=float(os.getenv("AI_TEMPERATURE", "0.8")),  # Увеличили с 0.7 до 0.8 для скорости
            ai_max_tokens=int(os.getenv("AI_MAX_TOKENS", "256")),  # Уменьшили с 512 до 256
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "bot.log"),
            company_name=os.getenv("COMPANY_NAME", "Ваша Компания"),
        )


@beartype
def get_config() -> Config:
    """Получить глобальную конфигурацию приложения.

    Returns:
        Config: Объект конфигурации
    """
    return Config.from_env()
