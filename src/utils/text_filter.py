"""Фильтрация и очистка текста от английских слов и ошибок."""

from __future__ import annotations

import re

# NOTE: beartype декораторы временно отключены из-за UnicodeEncodeError в Windows
# from beartype import beartype

# Словарь замен частых английских слов на русские
ENGLISH_TO_RUSSIAN = {
    # Время и опыт
    "years": "лет",
    "year": "год",
    "experience": "опыт",
    "month": "месяц",
    "months": "месяцев",
    "day": "день",
    "days": "дней",
    
    # Бизнес термины
    "service": "услуга",
    "services": "услуги",
    "quality": "качество",
    "support": "поддержка",
    "response": "отклик",
    "offer": "предложение",
    "offers": "предложения",
    "price": "цена",
    "cost": "стоимость",
    "project": "проект",
    "projects": "проекты",
    "solution": "решение",
    "solutions": "решения",
    "client": "клиент",
    "clients": "клиенты",
    "customer": "покупатель",
    "customers": "покупатели",
    
    # Действия
    "help": "помощь",
    "call": "звонок",
    "contact": "контакт",
    "contacts": "контакты",
    "work": "работа",
    "working": "работаем",
    "provide": "предоставляем",
    "deliver": "доставляем",
    "repeat": "повторить",
    "again": "снова",
    "said": "сказал",
    "say": "сказать",
    "tell": "сказать",
    "talk": "говорить",
    "discuss": "обсудить",
    "ask": "спросить",
    "know": "знать",
    
    # Прилагательные
    "best": "лучший",
    "good": "хороший",
    "fast": "быстрый",
    "quick": "быстрый",
    "professional": "профессиональный",
    "individual": "индивидуальный",
    "personal": "личный",
    "reliable": "надежный",
    "new": "новый",
    "old": "старый",
    
    # Другое
    "team": "команда",
    "company": "компания",
    "business": "бизнес",
    "details": "детали",
    "information": "информация",
    "question": "вопрос",
    "questions": "вопросы",
    "answer": "ответ",
    "answers": "ответы",
    "please": "пожалуйста",
    "thanks": "спасибо",
    "yes": "да",
    "no": "нет",
    "okay": "хорошо",
    "ok": "хорошо",
}

# Частые грамматические ошибки
COMMON_ERRORS = {
    "реагировка": "реакция",
    "реагировки": "реакции",
    "реагировку": "реакцию",
    "реагировкой": "реакцией",
    "специалисти": "специалисты",
    "físикой": "физикой",
    "físика": "физика",
    "físике": "физике",
    "físику": "физику",
    "físики": "физики",
    "угмах": "услугах",
    "угмами": "услугами",
    "угм": "услуг",
    "угме": "услуге",
}


def filter_english_words(text: str) -> str:
    """Удалить/заменить английские слова в тексте.
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Очищенный текст без английских слов
    """
    if not text:
        return text
    
    # 1. Замена по словарю (case-insensitive) - только целые слова
    for eng, rus in ENGLISH_TO_RUSSIAN.items():
        # Заменяем целые слова, учитывая границы слов
        pattern = rf'\b{re.escape(eng)}\b'
        text = re.sub(pattern, rus, text, flags=re.IGNORECASE)
    
    # 2. Удаление английских букв вставленных внутрь слов (например "выagain" -> "вы")
    # Сначала удаляем латинские буквы НЕ окруженные пробелами
    # Паттерн: латинские буквы окруженные с обеих сторон не-пробелами
    text = re.sub(r'(?<=[^\s])[a-zA-Z]+(?=[^\s])', '', text)
    text = re.sub(r'(?<=[^\s])[a-zA-Z]+\s', ' ', text)  # "словоagain " -> "слово "
    text = re.sub(r'\s[a-zA-Z]+(?=[^\s])', ' ', text)   # " againслово" -> " слово"
    
    # 3. Удаление оставшихся полных английских слов (целые слова с границами)
    text = re.sub(r'\b[a-zA-Z]{2,}\b', '', text)
    
    # 4. Очистка множественных пробелов и лишних пробелов
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Убрать пробел перед знаками
    text = text.strip()
    
    return text


def fix_common_errors(text: str) -> str:
    """Исправить частые грамматические ошибки.
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Текст с исправленными ошибками
    """
    if not text:
        return text
    
    # Замена частых ошибок с использованием границ слов
    for wrong, correct in COMMON_ERRORS.items():
        # Используем regex с границами слов для точной замены
        pattern = rf'\b{re.escape(wrong)}\b'
        text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
    
    return text


def format_text_with_line_breaks(text: str) -> str:
    """Простая и надежная разбивка текста на строки после предложений.
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Текст с переносами строк после каждого предложения
    """
    if not text:
        return text
    
    # Используем регулярное выражение для разбивки после предложений
    # Паттерн: знак препинания (. ! ?) + возможные эмодзи + пробел
    # Важно: знак препинания должен оставаться с предложением
    
    # Заменяем . ! ? (с эмодзи после них) на тот же текст + перенос строки
    # Паттерн: ([.!?]) - знак препинания
    #          ([^\w\s]*) - возможные эмодзи/символы после знака
    #          \s+ - пробелы
    result = re.sub(r'([.!?])([^\w\s]*)\s+', r'\1\2\n', text)
    
    # Убрать лишние пустые строки
    lines = [line.strip() for line in result.split('\n') if line.strip()]
    
    return '\n'.join(lines)


def clean_text(text: str) -> str:
    """Комплексная очистка текста: английские слова + грамматические ошибки + форматирование.
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Полностью очищенный и отформатированный текст
    """
    if not text:
        return text
    
    # Применяем все фильтры по очереди
    text = filter_english_words(text)
    text = fix_common_errors(text)
    text = format_text_with_line_breaks(text)  # Добавить переносы строк
    
    # Финальная очистка
    text = text.strip()
    
    return text
