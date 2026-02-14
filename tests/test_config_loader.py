"""Тесты для загрузчика конфигурации."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.utils.config_loader import BotConfig, ConfigError


def test_load_valid_config():
    """Проверка загрузки валидной конфигурации."""
    config_data = {
        "company": {
            "name": "Test Company",
            "phone": "+7 (999) 123-45-67",
            "email": "test@example.com",
            "telegram": "@test_manager"
        },
        "bot": {
            "welcome_message": "Привет от {company_name}!",
            "personality": "friendly",
            "sales_strategy": "soft",
            "language": "ru",
            "max_response_length": 300
        },
        "ai": {
            "model": "llama3.2:3b",
            "temperature": 0.5,
            "max_tokens": 300,
            "context_messages": 5
        },
        "features": {
            "quick_faq": True,
            "streaming": True,
            "progress_bar": True,
            "hints": False,
            "onboarding_tips": False
        },
        "faq": {
            "quick_check_threshold": 0.75,
            "search_threshold": 0.4,
            "max_results": 3
        }
    }
    
    # Создать временный файл конфигурации
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(config_data, f)
        temp_path = f.name
    
    try:
        config = BotConfig(temp_path)
        assert config.company_name == "Test Company"
        assert config.company_phone == "+7 (999) 123-45-67"
        assert config.ai_temperature == 0.5
        assert config.ai_max_tokens == 300
    finally:
        Path(temp_path).unlink()


def test_load_missing_file():
    """Проверка ошибки при отсутствии файла."""
    with pytest.raises(ConfigError, match="not found"):
        BotConfig("nonexistent_config.json")


def test_load_invalid_json():
    """Проверка ошибки при невалидном JSON."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        f.write("{ invalid json")
        temp_path = f.name
    
    try:
        with pytest.raises(ConfigError, match="Invalid JSON"):
            BotConfig(temp_path)
    finally:
        Path(temp_path).unlink()


def test_validation_missing_section():
    """Проверка валидации отсутствующей секции."""
    config_data = {
        "company": {
            "name": "Test",
            "phone": "+7",
            "email": "test@test.com",
            "telegram": "@test"
        }
        # Отсутствует секция "bot"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(config_data, f)
        temp_path = f.name
    
    try:
        with pytest.raises(ConfigError, match="Missing required section"):
            BotConfig(temp_path)
    finally:
        Path(temp_path).unlink()


def test_validation_invalid_temperature():
    """Проверка валидации температуры AI."""
    config_data = {
        "company": {"name": "Test", "phone": "+7", "email": "test@test.com", "telegram": "@test"},
        "bot": {"welcome_message": "Hi", "personality": "test", "sales_strategy": "test", "language": "ru", "max_response_length": 300},
        "ai": {"model": "test", "temperature": 1.5, "max_tokens": 300, "context_messages": 5},  # Невалидная температура
        "features": {"quick_faq": True, "streaming": True, "progress_bar": True, "hints": False, "onboarding_tips": False},
        "faq": {"quick_check_threshold": 0.75, "search_threshold": 0.4, "max_results": 3}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(config_data, f)
        temp_path = f.name
    
    try:
        with pytest.raises(ConfigError, match="temperature"):
            BotConfig(temp_path)
    finally:
        Path(temp_path).unlink()


def test_welcome_message_formatting():
    """Проверка форматирования приветственного сообщения."""
    config_data = {
        "company": {"name": "Test Company", "phone": "+7", "email": "test@test.com", "telegram": "@test"},
        "bot": {"welcome_message": "Привет от {company_name}!", "personality": "test", "sales_strategy": "test", "language": "ru", "max_response_length": 300},
        "ai": {"model": "test", "temperature": 0.5, "max_tokens": 300, "context_messages": 5},
        "features": {"quick_faq": True, "streaming": True, "progress_bar": True, "hints": False, "onboarding_tips": False},
        "faq": {"quick_check_threshold": 0.75, "search_threshold": 0.4, "max_results": 3}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(config_data, f)
        temp_path = f.name
    
    try:
        config = BotConfig(temp_path)
        assert config.welcome_message == "Привет от Test Company!"
    finally:
        Path(temp_path).unlink()
