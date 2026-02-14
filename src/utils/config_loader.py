"""Загрузчик конфигурации с валидацией."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from beartype import beartype

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Ошибка конфигурации."""
    pass


@beartype
class BotConfig:
    """Конфигурация бота."""
    
    def __init__(self, config_path: str | Path = "config.json") -> None:
        """Инициализация конфигурации.
        
        Args:
            config_path: Путь к файлу конфигурации
            
        Raises:
            ConfigError: При ошибке загрузки или валидации
        """
        self.config_path = Path(config_path)
        self._data: dict[str, Any] = {}
        self._load()
        self._validate()
    
    def _load(self) -> None:
        """Загрузить конфигурацию из файла."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
        except FileNotFoundError:
            raise ConfigError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {e}")
    
    def _validate(self) -> None:
        """Валидация конфигурации."""
        # Проверка обязательных секций
        required_sections = ["company", "bot", "ai", "features", "faq"]
        for section in required_sections:
            if section not in self._data:
                raise ConfigError(f"Missing required section: {section}")
        
        # Проверка обязательных полей компании
        company = self._data["company"]
        required_company_fields = ["name", "phone", "email", "telegram"]
        for field in required_company_fields:
            if not company.get(field):
                raise ConfigError(f"Missing required company field: {field}")
        
        # Проверка AI параметров
        ai = self._data["ai"]
        if not 0.0 <= ai.get("temperature", 0) <= 1.0:
            raise ConfigError("AI temperature must be between 0.0 and 1.0")
        if ai.get("max_tokens", 0) <= 0:
            raise ConfigError("AI max_tokens must be positive")
        if ai.get("context_messages", 0) <= 0:
            raise ConfigError("AI context_messages must be positive")
        
        # Проверка FAQ параметров
        faq = self._data["faq"]
        if not 0.0 <= faq.get("quick_check_threshold", 0) <= 1.0:
            raise ConfigError("FAQ quick_check_threshold must be between 0.0 and 1.0")
        if not 0.0 <= faq.get("search_threshold", 0) <= 1.0:
            raise ConfigError("FAQ search_threshold must be between 0.0 and 1.0")
    
    # Удобные геттеры
    @property
    def company_name(self) -> str:
        """Название компании."""
        return self._data["company"]["name"]
    
    @property
    def company_phone(self) -> str:
        """Телефон компании."""
        return self._data["company"]["phone"]
    
    @property
    def company_email(self) -> str:
        """Email компании."""
        return self._data["company"]["email"]
    
    @property
    def company_telegram(self) -> str:
        """Telegram компании."""
        return self._data["company"]["telegram"]
    
    @property
    def welcome_message(self) -> str:
        """Приветственное сообщение."""
        msg = self._data["bot"]["welcome_message"]
        return msg.format(company_name=self.company_name)
    
    @property
    def ai_model(self) -> str:
        """Модель AI."""
        return self._data["ai"]["model"]
    
    @property
    def ai_temperature(self) -> float:
        """Температура AI."""
        return self._data["ai"]["temperature"]
    
    @property
    def ai_max_tokens(self) -> int:
        """Максимальное количество токенов."""
        return self._data["ai"]["max_tokens"]
    
    @property
    def ai_context_messages(self) -> int:
        """Количество сообщений в контексте."""
        return self._data["ai"]["context_messages"]
    
    @property
    def quick_faq_enabled(self) -> bool:
        """Включена ли быстрая проверка FAQ."""
        return self._data["features"]["quick_faq"]
    
    @property
    def streaming_enabled(self) -> bool:
        """Включен ли streaming."""
        return self._data["features"]["streaming"]
    
    @property
    def faq_quick_threshold(self) -> float:
        """Порог для быстрой проверки FAQ."""
        return self._data["faq"]["quick_check_threshold"]
    
    @property
    def faq_search_threshold(self) -> float:
        """Порог для поиска FAQ."""
        return self._data["faq"]["search_threshold"]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение из конфигурации.
        
        Args:
            key: Ключ (может быть вложенным, например "company.name")
            default: Значение по умолчанию
            
        Returns:
            Any: Значение или default
        """
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
