"""Расширенная система классификации интентов с приоритизацией.

Реализует полную таксономию интентов по универсальному стандарту качества.
Использует каскадный подход с приоритизацией: супер-приоритетные интенты
(безопасность, данные, претензии) проверяются первыми.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

from beartype import beartype
from src.database.context import Message

if TYPE_CHECKING:
    pass


class IntentPriority(IntEnum):
    """Приоритеты интентов (чем меньше число, тем выше приоритет)."""

    SECURITY = 1  # Безопасность/абьюз
    PRIVACY = 2  # Запросы по данным
    COMPLAINTS = 3  # Возвраты/претензии
    TRANSACTIONS = 4  # Транзакции
    PRESALES = 5  # Предпродажа
    SUPPORT = 6  # Поддержка
    NAVIGATION = 7  # Навигация


@dataclass(frozen=True)
class Intent:
    """Результат классификации интента."""

    name: str
    priority: IntentPriority
    confidence: float  # 0.0 - 1.0
    group: str  # Группа интента для логирования


class IntentClassifier:
    """Классификатор интентов с каскадной приоритизацией."""

    # Определение всех интентов по группам (в порядке убывания приоритета)

    # Группа 1: Безопасность (супер-приоритет)
    SECURITY_INTENTS = {
        "abuse": [
            "мошенни",
            "обман",
            "кидал",
            "развод",
            "скам",
            "хакер",
            "взлом",
            "вирус",
        ],
        "aggression": [
            "сука",
            "блять",
            "пидор",
            "хуй",
            "ублюдок",
            "мудак",
            "гнида",
            "сволочь",
            "уебок",
            "убью",
            "убить",
            "угрож",
        ],
        "fraud_signals": [
            "дай пароль",
            "назови пароль",
            "данные клиента",
            "дай телефон",
            "телефон клиента",
            "покажи заказ",
            "заказ другого",
        ],
    }

    # Группа 2: Privacy/Данные
    PRIVACY_INTENTS = {
        "privacy_request": [
            "удалить данные",
            "удалите мои данные",
            "забыть меня",
            "право на забвение",
            "gdpr",
            "персональные данные",
            "запрос данных",
        ],
        "delete_data": [
            "удалить",
            "удалите",
            "стереть",
            "очистить историю",
            "забыть",
        ],
        "get_data_copy": [
            "выгрузить данные",
            "копия данных",
            "экспорт данных",
            "что вы знаете обо мне",
            "какие данные храните",
        ],
    }

    # Группа 3: Возвраты/Претензии
    COMPLAINTS_INTENTS = {
        "refund_request": [
            "возврат",
            "вернуть",
            "вернуть деньги",
            "верните деньги",
            "отменить заказ",
            "не хочу",
            "отказ от заказа",
        ],
        "complaint_quality": [
            "плохое качество",
            "не работает",
            "сломалось",
            "дефект",
            "брак",
            "некачественно",
            "не то что обещали",
        ],
        "complaint_service": [
            "плохой сервис",
            "не довольн",
            "жалоба",
            "претензия",
            "обманули",
            "не выполнили",
            "задержка",
        ],
    }

    # Группа 4: Транзакции
    TRANSACTIONS_INTENTS = {
        "buy": [
            "купить",
            "заказать",
            "оформить",
            "хочу заказать",
            "готов заказать",
            "оформляем",
        ],
        "payment": [
            "оплата",
            "оплатить",
            "как оплатить",
            "способ оплаты",
            "где платить",
            "счет",
        ],
        "invoice": [
            "счёт",
            "выставить счёт",
            "нужен счёт",
            "инвойс",
            "реквизиты",
        ],
        "appointment_booking": [
            "записаться",
            "запись",
            "назначить встречу",
            "консультация",
            "созвониться",
        ],
    }

    # Группа 5: Предпродажа
    PRESALES_INTENTS = {
        "services_browse": [
            "услуги",
            "что делаете",
            "чем занимаетесь",
            "направления",
            "сервисы",
            "предлагаете",
        ],
        "pricing_request": [
            "цена",
            "стоимость",
            "сколько стоит",
            "расценки",
            "прайс",
            "тариф",
            "бюджет",
        ],
        "timing_request": [
            "срок",
            "как долго",
            "когда",
            "время выполнения",
            "длительность",
            "как быстро",
        ],
        "comparison": [
            "сравнить",
            "разница",
            "отличие",
            "что лучше",
            "чем отличаетесь",
            "конкуренты",
        ],
        "objections": [
            "дорого",
            "долго",
            "не уверен",
            "подумать",
            "сомневаюсь",
            "не убедили",
        ],
    }

    # Группа 6: Поддержка
    SUPPORT_INTENTS = {
        "how_to": [
            "как",
            "инструкция",
            "не понятно",
            "не получается",
            "помогите",
            "подскажите",
        ],
        "status": [
            "статус",
            "где заказ",
            "отследить",
            "трек номер",
            "проверить заказ",
        ],
        "change_order": [
            "изменить",
            "поменять",
            "добавить",
            "убрать",
            "изменить заказ",
        ],
        "cancel_order": ["отменить", "не нужен", "отмена заказа"],
    }

    # Группа 7: Навигация
    NAVIGATION_INTENTS = {
        "greet": [
            "привет",
            "здравствуй",
            "добрый день",
            "доброе утро",
            "добрый вечер",
            "hi",
            "hello",
        ],
        "menu": ["меню", "главная", "разделы", "что умеешь"],
        "help": ["помощь", "справка", "что делать", "не понимаю"],
        "human_handoff": [
            "менеджер",
            "оператор",
            "человек",
            "специалист",
            "живой",
            "хочу с человеком",
        ],
    }

    @beartype
    def __init__(self) -> None:
        """Инициализация классификатора."""
        # Собираем все интенты в один список для быстрого доступа
        self._all_intents = self._build_intent_registry()

    def _build_intent_registry(self) -> list[tuple[str, IntentPriority, str, list[str]]]:
        """Построить реестр всех интентов с их приоритетами.

        Returns:
            list: [(intent_name, priority, group, keywords), ...]
        """
        registry = []

        # Безопасность
        for intent_name, keywords in self.SECURITY_INTENTS.items():
            registry.append((intent_name, IntentPriority.SECURITY, "security", keywords))

        # Privacy
        for intent_name, keywords in self.PRIVACY_INTENTS.items():
            registry.append((intent_name, IntentPriority.PRIVACY, "privacy", keywords))

        # Претензии
        for intent_name, keywords in self.COMPLAINTS_INTENTS.items():
            registry.append(
                (intent_name, IntentPriority.COMPLAINTS, "complaints", keywords)
            )

        # Транзакции
        for intent_name, keywords in self.TRANSACTIONS_INTENTS.items():
            registry.append(
                (intent_name, IntentPriority.TRANSACTIONS, "transactions", keywords)
            )

        # Предпродажа
        for intent_name, keywords in self.PRESALES_INTENTS.items():
            registry.append(
                (intent_name, IntentPriority.PRESALES, "presales", keywords)
            )

        # Поддержка
        for intent_name, keywords in self.SUPPORT_INTENTS.items():
            registry.append((intent_name, IntentPriority.SUPPORT, "support", keywords))

        # Навигация
        for intent_name, keywords in self.NAVIGATION_INTENTS.items():
            registry.append(
                (intent_name, IntentPriority.NAVIGATION, "navigation", keywords)
            )

        # Сортируем по приоритету (от высшего к низшему)
        registry.sort(key=lambda x: x[1])
        return registry

    @beartype
    def classify(
        self, text: str, conversation_history: list[Message] | None = None
    ) -> Intent:
        """Классифицировать интент пользователя.

        Использует каскадный подход: сначала проверяются интенты с высшим приоритетом.
        Как только найдено совпадение с достаточной уверенностью, поиск останавливается.

        Args:
            text: Текст сообщения пользователя
            conversation_history: История диалога для контекста

        Returns:
            Intent: Классифицированный интент с confidence
        """
        text_lower = text.lower()

        # Каскадная проверка по приоритетам
        for intent_name, priority, group, keywords in self._all_intents:
            confidence = self._calculate_confidence(text_lower, keywords)

            if confidence > 0.0:
                # Для супер-приоритетных интентов (безопасность, privacy, претензии)
                # даже низкий confidence приводит к срабатыванию
                if priority <= IntentPriority.COMPLAINTS:
                    return Intent(
                        name=intent_name,
                        priority=priority,
                        confidence=confidence,
                        group=group,
                    )

                # Для остальных интентов требуем минимальный порог
                if confidence >= 0.3:
                    return Intent(
                        name=intent_name,
                        priority=priority,
                        confidence=confidence,
                        group=group,
                    )

        # Если ничего не найдено - возвращаем дефолтный интент "general"
        return Intent(
            name="general",
            priority=IntentPriority.NAVIGATION,
            confidence=0.5,
            group="navigation",
        )

    @beartype
    def _calculate_confidence(self, text_lower: str, keywords: list[str]) -> float:
        """Рассчитать уверенность совпадения с ключевыми словами.

        Args:
            text_lower: Текст в нижнем регистре
            keywords: Список ключевых слов интента

        Returns:
            float: Уверенность от 0.0 до 1.0
        """
        matches = 0
        total_keywords = len(keywords)

        for keyword in keywords:
            if keyword in text_lower:
                matches += 1

        if matches == 0:
            return 0.0

        # Базовая confidence - доля совпавших keywords
        confidence = matches / total_keywords

        # Бонус если текст короткий и точный
        if len(text_lower.split()) <= 5 and matches > 0:
            confidence = min(confidence + 0.3, 1.0)

        return confidence

    @beartype
    def get_priority(self, intent: Intent) -> int:
        """Получить числовой приоритет интента.

        Args:
            intent: Интент

        Returns:
            int: Приоритет (чем меньше, тем важнее)
        """
        return int(intent.priority)

    @beartype
    def disambiguate(self, candidates: list[Intent]) -> Intent | None:
        """Разрешить неоднозначность между несколькими интентами.

        Args:
            candidates: Список кандидатов-интентов

        Returns:
            Intent | None: Лучший интент или None если невозможно определить
        """
        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        # Сортируем по приоритету, затем по confidence
        candidates_sorted = sorted(
            candidates, key=lambda i: (i.priority, -i.confidence)
        )

        # Берём топ-2
        top1 = candidates_sorted[0]
        top2 = candidates_sorted[1] if len(candidates_sorted) > 1 else None

        # Если у top1 значительно выше приоритет или confidence - выбираем его
        if top2 is None:
            return top1

        if top1.priority < top2.priority:
            return top1  # Приоритет важнее

        if top1.confidence - top2.confidence > 0.2:
            return top1  # Значительно больше уверенность

        # Иначе неоднозначность
        return None

    @beartype
    def requires_immediate_handoff(self, intent: Intent) -> bool:
        """Проверить, требует ли интент немедленной эскалации к менеджеру.

        Args:
            intent: Интент

        Returns:
            bool: True если требуется handoff
        """
        # Супер-приоритетные интенты всегда требуют handoff
        return intent.priority <= IntentPriority.COMPLAINTS

    @beartype
    def get_handoff_reason(self, intent: Intent) -> str:
        """Получить причину handoff для интента.

        Args:
            intent: Интент

        Returns:
            str: Текстовое описание причины
        """
        reasons = {
            "abuse": "Попытка обмана или злоупотребления",
            "aggression": "Агрессивное поведение клиента",
            "fraud_signals": "Подозрение на фишинг/мошенничество",
            "privacy_request": "Запрос по персональным данным",
            "delete_data": "Запрос на удаление данных (GDPR/152-ФЗ)",
            "get_data_copy": "Запрос на выгрузку данных (GDPR)",
            "refund_request": "Запрос на возврат средств",
            "complaint_quality": "Жалоба на качество",
            "complaint_service": "Жалоба на сервис",
        }

        return reasons.get(intent.name, "Требуется участие специалиста")
