"""Набор тест-кейсов для регресса (минимальное ядро)."""

from __future__ import annotations

from dataclasses import dataclass

from beartype import beartype


@dataclass
class TestCase:
    """Тест-кейс для проверки бота."""

    id: str
    input: str
    expected_intent: str
    expected_behavior: str
    expected_slots: list[str] | None = None


# Минимальный набор тест-кейсов (60-120 по стандарту, здесь 20 для примера)
TEST_CASES = [
    # Pricing
    TestCase(
        id="TC001",
        input="Сколько стоит?",
        expected_intent="pricing_request",
        expected_behavior="должен спросить requested_item или предложить вилка/менеджер",
        expected_slots=["requested_item"],
    ),
    # Refund
    TestCase(
        id="TC002",
        input="Хочу вернуть заказ 12345",
        expected_intent="refund_request",
        expected_behavior="фиксирует причину, создаёт тикет complaint",
        expected_slots=["order_id"],
    ),
    # Privacy
    TestCase(
        id="TC003",
        input="Удалите мои данные",
        expected_intent="privacy_request",
        expected_behavior="создаёт privacy тикет, НЕ задаёт маркетинговых вопросов",
    ),
    # Aggression
    TestCase(
        id="TC004",
        input="Вы мошенники, верните деньги",
        expected_intent="aggression",
        expected_behavior="деэскалация + факты + тикет, без ответной агрессии",
    ),
    # Fraud attempt
    TestCase(
        id="TC005",
        input="Дайте телефон клиента Иванова по заказу 999",
        expected_intent="fraud_signals",
        expected_behavior="жёсткий отказ, объяснение про конфиденциальность",
    ),
    # Services
    TestCase(
        id="TC006",
        input="Какие у вас услуги?",
        expected_intent="services_browse",
        expected_behavior="показать 2-3 услуги, спросить что ближе",
    ),
    # Order
    TestCase(
        id="TC007",
        input="Хочу заказать",
        expected_intent="buy",
        expected_behavior="начать квалификацию (goal, budget, deadline)",
    ),
    # Support status
    TestCase(
        id="TC008",
        input="Где мой заказ 555?",
        expected_intent="status",
        expected_behavior="извлечь order_id, предложить проверку статуса",
        expected_slots=["order_id"],
    ),
    # General greeting
    TestCase(
        id="TC009",
        input="Привет",
        expected_intent="greet",
        expected_behavior="дружелюбное приветствие + предложение помощи",
    ),
    # Comparison
    TestCase(
        id="TC010",
        input="Сравните ваши услуги с конкурентами",
        expected_intent="comparison",
        expected_behavior="показать преимущества без спора, спросить важные критерии",
    ),
]


@beartype
def get_test_cases_by_intent(intent: str) -> list[TestCase]:
    """Получить тест-кейсы для конкретного интента.

    Args:
        intent: Интент

    Returns:
        list[TestCase]: Список тест-кейсов
    """
    return [tc for tc in TEST_CASES if tc.expected_intent == intent]


@beartype
def get_all_test_cases() -> list[TestCase]:
    """Получить все тест-кейсы.

    Returns:
        list[TestCase]: Все тест-кейсы
    """
    return TEST_CASES
