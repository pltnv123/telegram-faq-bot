"""Умный fallback для ответов на общие вопросы без точного совпадения в FAQ."""

from __future__ import annotations

from beartype import beartype

from src.database.context import Message
from src.knowledge.faq_loader import KnowledgeBase


# Паттерны приветствий
GREETING_PATTERNS = [
    "привет",
    "здравствуй",
    "добрый день",
    "добрый вечер",
    "доброе утро",
    "здрасте",
    "хай",
    "hi",
    "hello",
]

# Паттерны для определения общих вопросов о компании
GENERAL_COMPANY_QUESTIONS = [
    "чем занимаетесь",
    "что делаете",
    "чем занимается",
    "что за компания",
    "о компании",
    "расскажите о себе",
    "кто вы",
    "что вы",
    "ваша деятельность",
    "ваш бизнес",
    "кто такие",
    "ваш профиль",
    "направление",
    "сфера деятельности",
    # Добавлены варианты с "сервис"
    "о сервисе",
    "ваш сервис",
    "вашем сервисе",
    "сервис",
    "расскажите о",
    "расскажи о",
    "о ваших",
    "что у вас",
]

# Паттерны для запросов деталей
DETAIL_REQUESTS = [
    "подробнее",
    "расскажи больше",
    "детальнее",
    "поподробнее",
    "еще",
    "дальше",
    "про",
    "расскажи о",
    "что насчет",
    "более детально",
    "развернуто",
    "полностью",
]

# Паттерны уточняющих вопросов
CLARIFICATION_PATTERNS = [
    "в смысле",
    "как это",
    "что значит",
    "не понял",
    "не понятно",
    "поясни",
    "объясни",
]

# Паттерны для вопросов о ценах
PRICING_QUESTIONS = [
    "сколько",
    "цена",
    "стоимость",
    "прайс",
    "расценки",
    "тариф",
    "оплата",
]


@beartype
def detect_general_intent(query: str) -> str | None:
    """Определить общее намерение если FAQ не нашел точного ответа.

    Args:
        query: Текст запроса пользователя

    Returns:
        str | None: Код намерения или None если не определено
    """
    query_lower = query.lower()

    # Приветствия
    if any(phrase in query_lower for phrase in GREETING_PATTERNS):
        return "greeting"

    # Уточняющие вопросы
    if any(phrase in query_lower for phrase in CLARIFICATION_PATTERNS):
        return "clarification"

    # Вопросы о компании и деятельности
    if any(phrase in query_lower for phrase in GENERAL_COMPANY_QUESTIONS):
        return "company_overview"

    # Запрос деталей (подробнее, еще, расскажи больше)
    if any(phrase in query_lower for phrase in DETAIL_REQUESTS):
        return "more_details"

    # Вопросы о ценах (общий обзор)
    if any(phrase in query_lower for phrase in PRICING_QUESTIONS):
        return "pricing_overview"

    return None


@beartype
def generate_fallback_response(
    intent: str,
    knowledge_base: KnowledgeBase,
    conversation_history: list[Message],
) -> str | None:
    """Генерировать умный fallback ответ на основе намерения.

    Args:
        intent: Определенное намерение (greeting, company_overview, more_details, pricing_overview, clarification)
        knowledge_base: База знаний
        conversation_history: История диалога

    Returns:
        str | None: Сгенерированный ответ или None
    """
    if intent == "greeting":
        return format_greeting_response(knowledge_base)

    elif intent == "clarification":
        # Если клиент не понял - повторяем суть более развернуто
        return format_company_overview(knowledge_base)

    elif intent == "company_overview":
        return format_company_overview(knowledge_base)

    elif intent == "more_details":
        # Анализируем контекст - о чем говорили
        last_topic = extract_last_topic(conversation_history)
        
        if last_topic == "services":
            return format_services_details(knowledge_base)
        elif last_topic == "pricing":
            return format_pricing_overview(knowledge_base)
        else:
            # Если контекст неясен - даем обзор компании
            return format_company_overview(knowledge_base)

    elif intent == "pricing_overview":
        return format_pricing_overview(knowledge_base)

    return None


@beartype
def format_greeting_response(kb: KnowledgeBase) -> str:
    """Дружелюбный ответ на приветствие.

    Args:
        kb: База знаний

    Returns:
        str: Форматированный ответ
    """
    return f"""Привет! Рад знакомству!

Я помогу вам узнать о {kb.company.name}. У нас {len(kb.services)} основных направления работы.

Что вас интересует?
• Наши услуги и что мы делаем
• Цены и сроки работы
• Как с нами связаться
• Примеры наших проектов

Просто спросите меня о чем угодно!"""


@beartype
def format_company_overview(kb: KnowledgeBase) -> str:
    """Сформатировать подробный ответ о компании и услугах.

    Args:
        kb: База знаний

    Returns:
        str: Форматированный ответ
    """
    # Краткий список услуг с эмодзи для живости
    services_list = "\n".join(
        [f"✓ {s.name} - {s.description}" for s in kb.services]
    )

    return f"""Отличный вопрос! Расскажу о нас.

{kb.company.name} - {kb.company.description}

Мы предлагаем:
{services_list}

Каждая услуга адаптируется под ваши задачи. Цены начинаются от 5000 руб.

Что вас интересует больше всего? Могу рассказать подробнее о любом направлении или обсудим ваш проект?"""


@beartype
def format_services_details(kb: KnowledgeBase) -> str:
    """Сформатировать детальное описание всех услуг.

    Args:
        kb: База знаний

    Returns:
        str: Форматированный ответ
    """
    details = []
    for service in kb.services:
        benefits = "\n  - ".join(service.benefits)
        details.append(
            f"""{service.name}
{service.description}

Цена: {service.price}
Срок: {service.duration}
Преимущества:
  - {benefits}
"""
        )

    result = "\n".join(details)
    return f"""{result}

Какая услуга вас заинтересовала больше всего? Или хотите обсудить ваш проект подробнее?"""


@beartype
def format_pricing_overview(kb: KnowledgeBase) -> str:
    """Сформатировать общий обзор цен.

    Args:
        kb: База знаний

    Returns:
        str: Форматированный ответ
    """
    pricing = "\n".join(
        [f"• {s.name}: {s.price} (срок: {s.duration})" for s in kb.services]
    )

    return f"""Вот наши цены:

{pricing}

Точная стоимость зависит от объема работ. Первичная консультация (30 мин) - бесплатно.

Хотите обсудить ваш проект и получить точную оценку? Свяжитесь со мной:
- Telegram: {kb.company.telegram}
- Телефон: {kb.company.phone}
- Email: {kb.company.email}"""


@beartype
def extract_last_topic(conversation_history: list[Message]) -> str | None:
    """Извлечь последнюю обсуждаемую тему из истории диалога.

    Args:
        conversation_history: История сообщений

    Returns:
        str | None: Название темы или None
    """
    if not conversation_history:
        return None

    # Анализируем последние 2-3 сообщения
    recent = conversation_history[-3:]

    topics = {
        "services": ["услуг", "сервис", "делаете", "предлагаете", "занимаетесь"],
        "pricing": ["цен", "стоимость", "прайс", "руб", "стоит"],
        "timing": ["срок", "долго", "быстро", "время", "когда"],
        "contacts": ["контакт", "связь", "телефон", "email"],
    }

    for msg in reversed(recent):
        content_lower = msg.content.lower()
        for topic, keywords in topics.items():
            if any(kw in content_lower for kw in keywords):
                return topic

    return None
