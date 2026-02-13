"""Загрузка и управление базой знаний FAQ."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from beartype import beartype


@beartype
@dataclass(frozen=True)
class Company:
    """Информация о компании."""

    name: str
    description: str
    website: str
    phone: str
    email: str
    telegram: str


@beartype
@dataclass(frozen=True)
class Service:
    """Описание услуги."""

    id: str
    name: str
    description: str
    price: str
    duration: str
    benefits: list[str]


@beartype
@dataclass(frozen=True)
class FAQItem:
    """Элемент FAQ."""

    id: int
    question: str
    answer: str
    category: str
    keywords: list[str]


@beartype
@dataclass(frozen=True)
class CommonPhrases:
    """Стандартные фразы бота."""

    greeting: str
    closing: str
    not_found: str
    error: str
    thinking: str


@beartype
@dataclass(frozen=True)
class KnowledgeBase:
    """База знаний FAQ."""

    company: Company
    services: list[Service]
    faq: list[FAQItem]
    phrases: CommonPhrases

    def get_service_by_id(self, service_id: str) -> Service | None:
        """Получить услугу по ID.

        Args:
            service_id: ID услуги

        Returns:
            Service | None: Услуга или None если не найдена
        """
        for service in self.services:
            if service.id == service_id:
                return service
        return None

    def get_faq_by_category(self, category: str) -> list[FAQItem]:
        """Получить FAQ по категории.

        Args:
            category: Название категории

        Returns:
            list[FAQItem]: Список элементов FAQ
        """
        return [item for item in self.faq if item.category == category]

    def get_all_categories(self) -> list[str]:
        """Получить список всех категорий FAQ.

        Returns:
            list[str]: Список уникальных категорий
        """
        return list({item.category for item in self.faq})


@beartype
class FAQLoader:
    """Загрузчик базы знаний из JSON файла."""

    def __init__(self, faq_path: Path) -> None:
        """Инициализация загрузчика.

        Args:
            faq_path: Путь к JSON файлу с FAQ
        """
        self.faq_path = faq_path
        self._cache: KnowledgeBase | None = None

    async def load(self) -> KnowledgeBase:
        """Загрузить базу знаний из файла.

        Returns:
            KnowledgeBase: Загруженная база знаний

        Raises:
            FileNotFoundError: Если файл не найден
            json.JSONDecodeError: Если файл содержит невалидный JSON
            ValueError: Если структура данных не соответствует ожиданиям
        """
        if self._cache is not None:
            return self._cache

        if not self.faq_path.exists():
            raise FileNotFoundError(f"FAQ файл не найден: {self.faq_path}")

        with open(self.faq_path, encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)

        # Парсинг данных компании
        company_data = data.get("company", {})
        contact_data = company_data.get("contact", {})
        company = Company(
            name=company_data.get("name", ""),
            description=company_data.get("description", ""),
            website=company_data.get("website", ""),
            phone=contact_data.get("phone", ""),
            email=contact_data.get("email", ""),
            telegram=contact_data.get("telegram", ""),
        )

        # Парсинг услуг
        services = [
            Service(
                id=s.get("id", ""),
                name=s.get("name", ""),
                description=s.get("description", ""),
                price=s.get("price", ""),
                duration=s.get("duration", ""),
                benefits=s.get("benefits", []),
            )
            for s in data.get("services", [])
        ]

        # Парсинг FAQ
        faq_items = [
            FAQItem(
                id=item.get("id", 0),
                question=item.get("question", ""),
                answer=item.get("answer", ""),
                category=item.get("category", "general"),
                keywords=item.get("keywords", []),
            )
            for item in data.get("faq", [])
        ]

        # Парсинг стандартных фраз
        phrases_data = data.get("common_phrases", {})
        phrases = CommonPhrases(
            greeting=phrases_data.get("greeting", "Здравствуйте!"),
            closing=phrases_data.get("closing", "До свидания!"),
            not_found=phrases_data.get("not_found", "Ответ не найден."),
            error=phrases_data.get("error", "Произошла ошибка."),
            thinking=phrases_data.get("thinking", "Думаю..."),
        )

        self._cache = KnowledgeBase(
            company=company,
            services=services,
            faq=faq_items,
            phrases=phrases,
        )

        return self._cache

    def clear_cache(self) -> None:
        """Очистить кэш (для перезагрузки базы знаний)."""
        self._cache = None
