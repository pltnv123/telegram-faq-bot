"""Определение намерений пользователя для контекстных ответов."""

from __future__ import annotations

from beartype import beartype


@beartype
def detect_user_intent(text: str) -> str:
    """Определить намерение пользователя по тексту сообщения.

    Args:
        text: Текст сообщения пользователя

    Returns:
        str: Код намерения (pricing, services, contacts, order, general)
    """
    text_lower = text.lower()

    # Вопросы о ценах и стоимости
    pricing_keywords = [
        "сколько", "цена", "стоимость", "стоит", "расценки", "тариф",
        "прайс", "оплата", "бесплатно", "дорого", "дешево", "цены"
    ]
    if any(keyword in text_lower for keyword in pricing_keywords):
        return "pricing"

    # Вопросы об услугах
    services_keywords = [
        "услуга", "услуги", "делаете", "предлагаете", "сервис",
        "что вы", "чем занимаетесь", "направления", "работы"
    ]
    if any(keyword in text_lower for keyword in services_keywords):
        return "services"

    # Вопросы о контактах и связи
    contacts_keywords = [
        "связаться", "контакт", "телефон", "email", "почта", "адрес",
        "где находитесь", "как найти", "telegram", "написать", "позвонить"
    ]
    if any(keyword in text_lower for keyword in contacts_keywords):
        return "contacts"

    # Намерение заказать/купить
    order_keywords = [
        "заказать", "купить", "оформить", "нужна", "нужно", "хочу заказать",
        "готов заказать", "интересует", "подать заявку"
    ]
    if any(keyword in text_lower for keyword in order_keywords):
        return "order"

    # По умолчанию - общий контекст
    return "general"


@beartype
def should_show_hints(response_text: str, intent: str) -> bool:
    """Определить нужно ли показывать подсказки после ответа.

    Args:
        response_text: Текст ответа бота
        intent: Определенное намерение

    Returns:
        bool: True если нужно показать подсказки
    """
    # НЕ показываем hints если:
    
    # 1. Ответ короткий (простое подтверждение)
    if len(response_text) < 50:
        return False
    
    # 2. Уже есть контакты/телефон
    if any(word in response_text.lower() for word in ["телефон", "email", "telegram", "@"]):
        return False
    
    # 3. Есть список с маркерами (уже структурированный ответ)
    if "•" in response_text or "\n-" in response_text:
        return False
    
    # 4. Клиент задал конкретный вопрос (pricing, services, contacts, order)
    if intent in ["pricing", "services", "contacts", "order"]:
        return False
    
    # Показываем ТОЛЬКО для очень общих вопросов типа "привет"
    return False  # По умолчанию НЕ показываем
