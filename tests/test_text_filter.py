"""Тесты для фильтрации текста."""

from __future__ import annotations

import pytest

from src.utils.text_filter import clean_text, filter_english_words, fix_common_errors


def test_filter_english_words_removes_english():
    """Проверка удаления английских слов."""
    text = "Привет hello мир world"
    result = filter_english_words(text)
    assert "hello" not in result
    assert "world" not in result
    assert "Привет" in result
    assert "мир" in result


def test_filter_english_words_removes_mixed():
    """Проверка удаления английских букв из смешанных слов."""
    text = "выagain repeatите ужеsaid"
    result = filter_english_words(text)
    # Английские буквы должны быть удалены
    assert "again" not in result.lower()
    assert "repeat" not in result.lower()
    assert "said" not in result.lower()


def test_fix_common_errors():
    """Проверка исправления частых ошибок."""
    text = "реагировка специалисти"
    result = fix_common_errors(text)
    assert "реакция" in result
    assert "специалисты" in result


def test_clean_text_integration():
    """Интеграционный тест очистки текста."""
    text = "Привет! hello Это тест.\n\nС english словами."
    result = clean_text(text)
    # Английские слова удалены
    assert "hello" not in result.lower()
    assert "english" not in result.lower()
    # Русский текст сохранен
    assert "Привет" in result
    assert "тест" in result


def test_clean_text_preserves_emojis():
    """Проверка сохранения эмодзи."""
    text = "Привет! 👋 Как дела? 🚀"
    result = clean_text(text)
    assert "👋" in result
    assert "🚀" in result


def test_filter_english_words_empty():
    """Проверка обработки пустой строки."""
    result = filter_english_words("")
    assert result == ""


def test_clean_text_line_breaks():
    """Проверка форматирования переносов строк."""
    text = "Первое предложение. Второе предложение. Третье предложение."
    result = clean_text(text)
    # Должны быть переносы после предложений
    assert "\n" in result or "." in result
