"""Система извлечения слотов (параметров) из сообщений пользователя.

Извлекает обязательные параметры для каждого этапа воронки продаж.
Используется для structured data collection.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from beartype import beartype
from src.database.context import Message

if TYPE_CHECKING:
    pass


@dataclass
class SlotValue:
    """Значение слота с метаданными."""

    name: str
    value: str | None
    confidence: float  # 0.0 - 1.0
    extracted_from: str  # Откуда извлечено


@dataclass
class SlotCollection:
    """Коллекция извлечённых слотов."""

    slots: dict[str, SlotValue] = field(default_factory=dict)
    required_slots: list[str] = field(default_factory=list)

    @beartype
    def is_complete(self) -> bool:
        """Проверить заполнены ли все обязательные слоты."""
        for slot_name in self.required_slots:
            if slot_name not in self.slots or self.slots[slot_name].value is None:
                return False
        return True

    @beartype
    def get_missing_slots(self) -> list[str]:
        """Получить список незаполненных обязательных слотов."""
        missing = []
        for slot_name in self.required_slots:
            if slot_name not in self.slots or self.slots[slot_name].value is None:
                missing.append(slot_name)
        return missing

    @beartype
    def get_value(self, slot_name: str) -> str | None:
        """Получить значение слота."""
        if slot_name in self.slots:
            return self.slots[slot_name].value
        return None

    @beartype
    def set_value(self, slot_name: str, value: str, confidence: float = 1.0) -> None:
        """Установить значение слота."""
        self.slots[slot_name] = SlotValue(
            name=slot_name,
            value=value,
            confidence=confidence,
            extracted_from="manual",
        )


class SlotExtractor:
    """Экстрактор слотов из текста."""

    # Универсальные слоты по категориям

    # Слоты результата
    RESULT_SLOTS = ["goal", "desired_outcome", "requested_item"]

    # Слоты ограничений
    CONSTRAINT_SLOTS = ["deadline", "budget_band", "location", "constraints", "quantity"]

    # Операционные слоты
    OPERATIONAL_SLOTS = [
        "order_id",
        "account_id",
        "contact_channel",
        "contact",
        "consent_flag",
    ]

    # Паттерны для извлечения

    # Order ID паттерны
    ORDER_ID_PATTERNS = [
        r"заказ\s*№?\s*(\d+)",
        r"заказа?\s*(\d+)",
        r"номер\s*(\d+)",
        r"#(\d+)",
    ]

    # Budget паттерны
    BUDGET_PATTERNS = [
        r"(\d+)\s*(?:руб|рублей|тысяч|тыс|к)",
        r"бюджет\s*(\d+)",
        r"до\s*(\d+)",
        r"около\s*(\d+)",
    ]

    # Deadline паттерны
    DEADLINE_PATTERNS = [
        r"через\s+(\d+)\s+(?:день|дня|дней|неделю|недели|недель|месяц|месяца|месяцев)",
        r"до\s+(\d+)",
        r"срочно",
        r"как можно скорее",
        r"сегодня",
        r"завтра",
    ]

    # Contact паттерны
    PHONE_PATTERNS = [
        r"\+?7\s*\(?\d{3}\)?\s*\d{3}-?\d{2}-?\d{2}",
        r"8\s*\(?\d{3}\)?\s*\d{3}-?\d{2}-?\d{2}",
    ]

    EMAIL_PATTERNS = [
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    ]

    @beartype
    def __init__(self) -> None:
        """Инициализация экстрактора."""
        pass

    @beartype
    def extract(
        self,
        text: str,
        conversation_history: list[Message] | None = None,
        required_slots: list[str] | None = None,
    ) -> SlotCollection:
        """Извлечь слоты из текста.

        Args:
            text: Текст сообщения
            conversation_history: История для контекста
            required_slots: Список обязательных слотов

        Returns:
            SlotCollection: Коллекция извлечённых слотов
        """
        collection = SlotCollection(required_slots=required_slots or [])

        text_lower = text.lower()

        # Извлечение order_id
        order_id = self._extract_order_id(text)
        if order_id:
            collection.slots["order_id"] = SlotValue(
                name="order_id",
                value=order_id,
                confidence=0.9,
                extracted_from=text,
            )

        # Извлечение budget
        budget = self._extract_budget(text_lower)
        if budget:
            collection.slots["budget_band"] = SlotValue(
                name="budget_band",
                value=budget,
                confidence=0.8,
                extracted_from=text,
            )

        # Извлечение deadline
        deadline = self._extract_deadline(text_lower)
        if deadline:
            collection.slots["deadline"] = SlotValue(
                name="deadline",
                value=deadline,
                confidence=0.7,
                extracted_from=text,
            )

        # Извлечение контактов
        contact = self._extract_contact(text)
        if contact:
            collection.slots["contact"] = SlotValue(
                name="contact",
                value=contact,
                confidence=0.95,
                extracted_from=text,
            )

        # Извлечение goal (простая эвристика)
        goal = self._extract_goal(text_lower, conversation_history)
        if goal:
            collection.slots["goal"] = SlotValue(
                name="goal",
                value=goal,
                confidence=0.6,
                extracted_from=text,
            )

        return collection

    @beartype
    def _extract_order_id(self, text: str) -> str | None:
        """Извлечь номер заказа."""
        for pattern in self.ORDER_ID_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        return None

    @beartype
    def _extract_budget(self, text_lower: str) -> str | None:
        """Извлечь бюджет."""
        for pattern in self.BUDGET_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                amount = match.group(1)
                # Определить единицу измерения
                if "тысяч" in text_lower or "тыс" in text_lower or "к" in text_lower:
                    return f"{amount}000 руб"
                return f"{amount} руб"
        return None

    @beartype
    def _extract_deadline(self, text_lower: str) -> str | None:
        """Извлечь срок."""
        if "срочно" in text_lower:
            return "срочно"
        if "сегодня" in text_lower:
            return "сегодня"
        if "завтра" in text_lower:
            return "завтра"

        for pattern in self.DEADLINE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(0)

        return None

    @beartype
    def _extract_contact(self, text: str) -> str | None:
        """Извлечь контакт (телефон или email)."""
        # Проверка телефона
        for pattern in self.PHONE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        # Проверка email
        for pattern in self.EMAIL_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return None

    @beartype
    def _extract_goal(
        self, text_lower: str, conversation_history: list[Message] | None
    ) -> str | None:
        """Извлечь цель (простая эвристика на основе keywords)."""
        # Простые паттерны целей
        goal_patterns = {
            "консультация": ["консультация", "посоветовать", "помочь разобраться"],
            "разработка": ["разработать", "создать", "сделать сайт", "приложение"],
            "поддержка": [
                "поддержка",
                "сопровождение",
                "обслуживание",
                "техподдержка",
            ],
            "автоматизация": ["автоматизировать", "автоматизация", "оптимизировать"],
        }

        for goal_name, keywords in goal_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return goal_name

        return None

    @beartype
    def ask_next_missing(self, collection: SlotCollection) -> str:
        """Сформировать вопрос для запроса следующего недостающего слота.

        Args:
            collection: Коллекция слотов

        Returns:
            str: Текст вопроса пользователю
        """
        missing = collection.get_missing_slots()

        if not missing:
            return ""

        # Берём первый недостающий слот
        next_slot = missing[0]

        # Вопросы для каждого типа слота
        questions = {
            "goal": "Какая у вас цель? Что именно нужно сделать?",
            "desired_outcome": "Какой результат хотите получить?",
            "requested_item": "Что именно вас интересует из наших услуг?",
            "deadline": "Когда нужно? Есть ли срок?",
            "budget_band": "Какой у вас бюджет? Хотя бы примерно.",
            "location": "Где находитесь? В каком городе?",
            "constraints": "Есть ли какие-то обязательные условия или ограничения?",
            "quantity": "Какой объём работ? Сколько нужно?",
            "contact": "Оставьте контакт для связи (телефон или email).",
            "order_id": "Напишите номер заказа.",
        }

        question = questions.get(next_slot, f"Уточните: {next_slot}")

        # Если несколько слотов - можем объединить в один вопрос
        if len(missing) > 1:
            # Объединяем до 3 вопросов максимум
            combined_questions = []
            for slot in missing[:3]:
                if slot in questions:
                    combined_questions.append(questions[slot])

            if len(combined_questions) > 1:
                return f"{combined_questions[0]} И {combined_questions[1].lower()}"

        return question

    @beartype
    def validate_slot(self, slot_name: str, value: str) -> tuple[bool, str]:
        """Валидировать значение слота.

        Args:
            slot_name: Имя слота
            value: Значение

        Returns:
            tuple[bool, str]: (валидно, сообщение об ошибке)
        """
        # Валидация контактов
        if slot_name == "contact":
            if not value:
                return False, "Контакт не может быть пустым"

            # Проверка телефона или email
            is_phone = any(
                re.match(pattern, value) for pattern in self.PHONE_PATTERNS
            )
            is_email = any(
                re.match(pattern, value) for pattern in self.EMAIL_PATTERNS
            )

            if not is_phone and not is_email:
                return False, "Укажите корректный телефон или email"

        # Валидация order_id
        if slot_name == "order_id":
            if not value or not value.isdigit():
                return False, "Номер заказа должен быть числом"

        # Валидация budget
        if slot_name == "budget_band":
            if not any(char.isdigit() for char in value):
                return False, "Укажите бюджет числом"

        return True, ""

    @beartype
    def get_slot_category(self, slot_name: str) -> str:
        """Получить категорию слота.

        Args:
            slot_name: Имя слота

        Returns:
            str: Категория (result/constraint/operational)
        """
        if slot_name in self.RESULT_SLOTS:
            return "result"
        elif slot_name in self.CONSTRAINT_SLOTS:
            return "constraint"
        elif slot_name in self.OPERATIONAL_SLOTS:
            return "operational"
        return "unknown"
