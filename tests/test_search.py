"""Тесты для поиска по FAQ."""

from __future__ import annotations

import pytest

from src.knowledge.faq_loader import FAQItem
from src.knowledge.search import calculate_relevance, normalize_text


def test_normalize_text():
    """Проверка нормализации текста."""
    text = "Привет, Мир! Как дела?"
    result = normalize_text(text)
    assert result == "привет мир как дела"
    
    # Множественные пробелы
    text = "Привет    Мир"
    result = normalize_text(text)
    assert result == "привет мир"


def test_calculate_relevance_exact_match():
    """Проверка точного совпадения вопроса."""
    faq = FAQItem(
        question="Какие у вас услуги?",
        answer="У нас три вида услуг.",
        keywords=["услуги", "сервисы"],
        category="общее"
    )
    
    score = calculate_relevance("Какие у вас услуги?", faq)
    assert score >= 0.8  # Высокая релевантность


def test_calculate_relevance_partial_match():
    """Проверка частичного совпадения."""
    faq = FAQItem(
        question="Сколько стоит консультация?",
        answer="Консультация стоит от 5000 руб.",
        keywords=["цена", "стоимость"],
        category="цены"
    )
    
    score = calculate_relevance("консультация", faq)
    assert score > 0.0
    assert score < 1.0


def test_calculate_relevance_no_match():
    """Проверка отсутствия совпадения."""
    faq = FAQItem(
        question="Какие у вас услуги?",
        answer="У нас три вида услуг.",
        keywords=["услуги"],
        category="общее"
    )
    
    score = calculate_relevance("погода сегодня", faq)
    assert score < 0.3  # Низкая релевантность


def test_calculate_relevance_keyword_match():
    """Проверка совпадения по ключевым словам."""
    faq = FAQItem(
        question="Сколько стоит?",
        answer="Цены от 5000 руб.",
        keywords=["цена", "стоимость", "расценки"],
        category="цены"
    )
    
    score = calculate_relevance("какая цена", faq)
    assert score >= 0.7  # Высокая релевантность благодаря ключевому слову


def test_calculate_relevance_stop_words():
    """Проверка фильтрации стоп-слов."""
    faq = FAQItem(
        question="Как с вами связаться?",
        answer="Позвоните нам.",
        keywords=["контакты"],
        category="контакты"
    )
    
    # Запрос только из стоп-слов
    score = calculate_relevance("как где что", faq)
    assert score == 0.0  # Нет значимых слов


def test_calculate_relevance_case_insensitive():
    """Проверка нечувствительности к регистру."""
    faq = FAQItem(
        question="Какие услуги?",
        answer="Три вида услуг.",
        keywords=["УСЛУГИ"],
        category="общее"
    )
    
    score1 = calculate_relevance("УСЛУГИ", faq)
    score2 = calculate_relevance("услуги", faq)
    score3 = calculate_relevance("Услуги", faq)
    
    # Все варианты должны давать одинаковый результат
    assert score1 == score2 == score3
