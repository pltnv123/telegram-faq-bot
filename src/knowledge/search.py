"""Поиск по базе знаний FAQ (fallback режим без AI)."""

from __future__ import annotations

from beartype import beartype

from src.knowledge.faq_loader import FAQItem, KnowledgeBase


@beartype
def calculate_relevance(query: str, faq_item: FAQItem) -> float:
    """Рассчитать релевантность FAQ элемента к запросу.

    Args:
        query: Текст запроса пользователя
        faq_item: Элемент FAQ

    Returns:
        float: Оценка релевантности (0.0 - 1.0)
    """
    query_lower = query.lower()
    score = 0.0

    # Стоп-слова которые игнорируем (уменьшенный список для лучшего понимания)
    stop_words = {
        "как", "что", "где", "когда", "почему", "зачем", "какой", "какая", "какие",
        "это", "мне", "вы", "ты", "у", "в", "на", "с", "и", "или", "а", "но",
        "скажи", "можно", "нужно", "есть",
    }

    # Фильтруем стоп-слова и короткие слова
    query_words = [
        word for word in query_lower.split()
        if len(word) > 3 and word not in stop_words
    ]

    if not query_words:
        return 0.0

    # Проверка вопроса
    question_lower = faq_item.question.lower()
    if query_lower in question_lower:
        score += 1.0
    else:
        # Считаем сколько значимых слов совпало
        matched_words = sum(1 for word in query_words if word in question_lower)
        if matched_words > 0:
            score += 0.5 * (matched_words / len(query_words))

    # Проверка ключевых слов
    keywords_lower = [k.lower() for k in faq_item.keywords]
    for keyword in keywords_lower:
        if keyword in query_lower:
            score += 0.8
        else:
            # Частичное совпадение только значимых слов
            if any(word in keyword for word in query_words):
                score += 0.3

    # Проверка ответа (меньший вес)
    answer_lower = faq_item.answer.lower()
    if query_lower in answer_lower:
        score += 0.3
    else:
        matched_in_answer = sum(1 for word in query_words if word in answer_lower)
        if matched_in_answer > 0:
            score += 0.1 * (matched_in_answer / len(query_words))

    return min(score, 1.0)


@beartype
def quick_faq_check(
    query: str,
    knowledge_base: KnowledgeBase,
    min_score: float = 0.7,
) -> tuple[FAQItem, float] | None:
    """Быстрая проверка FAQ для мгновенных ответов на простые вопросы.
    
    Используется ДО AI генерации для быстрого ответа на точные совпадения.
    
    Args:
        query: Текст запроса пользователя
        knowledge_base: База знаний
        min_score: Минимальный порог релевантности (по умолчанию 0.7 - высокий)
    
    Returns:
        tuple[FAQItem, float] | None: FAQ элемент и score если найдено точное совпадение
    """
    if not knowledge_base.faq:
        return None
    
    # Поиск с высоким порогом
    scored_items = []
    for item in knowledge_base.faq:
        score = calculate_relevance(query, item)
        if score >= min_score:
            scored_items.append((item, score))
    
    if not scored_items:
        return None
    
    # Вернуть лучший результат
    scored_items.sort(key=lambda x: x[1], reverse=True)
    return scored_items[0]


@beartype
def search_faq(
    query: str,
    knowledge_base: KnowledgeBase,
    top_k: int = 3,
    min_score: float = 0.4,
) -> list[FAQItem]:
    """Поиск наиболее релевантных FAQ по запросу.

    Args:
        query: Текст запроса пользователя
        knowledge_base: База знаний
        top_k: Количество результатов для возврата
        min_score: Минимальный порог релевантности (по умолчанию 0.4)

    Returns:
        list[FAQItem]: Список наиболее релевантных FAQ элементов
    """
    if not query.strip():
        return []

    # Рассчитать релевантность для каждого FAQ элемента
    scored_items = [
        (faq_item, calculate_relevance(query, faq_item))
        for faq_item in knowledge_base.faq
    ]

    # Отфильтровать элементы с низкой релевантностью
    scored_items = [(item, score) for item, score in scored_items if score >= min_score]

    # Отсортировать по убыванию релевантности
    scored_items.sort(key=lambda x: x[1], reverse=True)

    # Вернуть top_k результатов
    return [item for item, _ in scored_items[:top_k]]


@beartype
def format_faq_results(faq_items: list[FAQItem]) -> str:
    """Отформатировать результаты поиска для отправки пользователю.

    Args:
        faq_items: Список найденных FAQ элементов

    Returns:
        str: Отформатированный текст ответа
    """
    if not faq_items:
        return ""

    if len(faq_items) == 1:
        # Один результат - просто вернуть ответ
        return faq_items[0].answer

    # Несколько результатов - показать все с нумерацией
    result = "Вот что я нашел по вашему запросу:\n\n"
    for i, item in enumerate(faq_items, 1):
        result += f"{i}. {item.question}\n{item.answer}\n\n"

    return result.strip()
