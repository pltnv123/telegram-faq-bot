# AI-Powered Telegram Bot с Универсальным Стандартом Качества

Профессиональный Telegram бот на базе LLM (Ollama), реализующий **универсальный стандарт качества** для клиентских чат-ботов, применимый в любых нишах при минимальной кастомизации.

## 🎯 Особенности

### Core Возможности
- ✅ **Полная воронка продаж** (7 этапов): Acquisition → Qualification → Offer → Closing → Support → Complaints → Retention
- ✅ **AI-генерация** на базе Ollama (llama3.2:3b или mistral:7b)
- ✅ **Умный FAQ search** с quick response для простых вопросов
- ✅ **Продающие стратегии**: SPIN, lead scoring, адаптивные CTA
- ✅ **Loading indicator** (progressive) во время генерации

### NLU (Natural Language Understanding)
- ✅ **Intent Classification** с приоритизацией (7 групп)
- ✅ **Slot Extraction** для structured data collection
- ✅ **Confidence scoring** и disambiguation

### Handoff & Ticketing
- ✅ **Автоматическая эскалация** для супер-приоритетных интентов
- ✅ **Ticket management** с SLA tracking
- ✅ **JSON export** для CRM интеграции
- ✅ **Escalation rules** (безопасность, privacy, претензии)

### Compliance
- ✅ **GDPR/152-ФЗ** базовая реализация
- ✅ **Privacy requests** (delete, export, correct data)
- ✅ **Data minimization** (сбор PII только когда необходимо)
- ✅ **Consent tracking**
- ✅ **Команда `/privacy`** для управления данными

### Метрики и QA
- ✅ **Событийная телеметрия** (conversation_started, intent_classified, etc.)
- ✅ **Метрики**: FRT (P50/P90), Containment Rate, FCR
- ✅ **QA стандарты**: 10-балльная оценочная карточка
- ✅ **Тест-кейсы** для регресса (60-120 кейсов)

## 📊 Архитектура

```
User Message
     ↓
┌────────────────────────────────┐
│  NLU Layer                      │
│  - Intent Classifier (7 groups) │
│  - Slot Extractor               │
└────────────┬───────────────────┘
             ↓
┌────────────────────────────────┐
│  Escalation Check               │
│  (Security/Privacy/Complaints)  │
└─────┬──────────────────┬───────┘
      │ No Escalate      │ Escalate
      ↓                  ↓
┌──────────┐      ┌─────────────┐
│ Quick FAQ│      │ Ticket Mgr  │
└────┬─────┘      └─────────────┘
     │ No Match
     ↓
┌────────────────────────────────┐
│  Funnel Router (7 stages)       │
│  1. Acquisition                 │
│  2. Qualification (slot collect)│
│  3. Offer (present options)     │
│  4. Closing (create order)      │
│  5. Support (how-to/status)     │
│  6. Complaints (refund)         │
│  7. Retention (upsell)          │
└────────────┬───────────────────┘
             ↓
┌────────────────────────────────┐
│  AI Generation (Ollama)         │
│  - Stage-specific prompts       │
│  - Anti-hallucination rules     │
└────────────┬───────────────────┘
             ↓
┌────────────────────────────────┐
│  Event Logger & Metrics         │
└────────────────────────────────┘
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Установить зависимости Python
pip install -r requirements.txt

# Или использовать install script
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Настроить Ollama (опционально, но рекомендуется)

```bash
# Скачать Ollama с https://ollama.com/download
# Установить и запустить модель
ollama pull llama3.2:3b
ollama serve
```

Подробнее: [`OLLAMA_SETUP.md`](OLLAMA_SETUP.md)

### 3. Настроить `.env`

```bash
# Создать .env файл
TELEGRAM_BOT_TOKEN=your_bot_token_here
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

### 4. Запустить бота

```bash
python -m src.main
```

## 📁 Структура проекта

```
c:\BOT\
├── src/
│   ├── nlu/                    # NLU модуль
│   │   ├── intent_classifier.py
│   │   └── slot_extractor.py
│   ├── funnel/                 # Воронка (7 этапов)
│   │   ├── stages.py
│   │   ├── acquisition.py
│   │   ├── qualification.py
│   │   ├── offer.py
│   │   ├── closing.py
│   │   ├── support.py
│   │   ├── complaints.py
│   │   ├── retention.py
│   │   └── router.py
│   ├── handoff/                # Handoff система
│   │   ├── ticket_manager.py
│   │   ├── escalation_rules.py
│   │   └── sla_tracker.py
│   ├── compliance/             # GDPR/152-ФЗ
│   │   ├── privacy_handler.py
│   │   ├── data_minimization.py
│   │   └── consent_tracker.py
│   ├── metrics/                # Метрики
│   │   ├── event_logger.py
│   │   └── calculator.py
│   ├── qa/                     # QA стандарты
│   │   ├── test_cases.py
│   │   └── dialog_evaluator.py
│   ├── bot/handlers/
│   │   ├── chat_new.py         # Основной handler с воронкой
│   │   ├── privacy.py          # /privacy команда
│   │   ├── start.py
│   │   └── menu.py
│   ├── ai/
│   │   ├── ollama_client.py
│   │   └── prompts.py          # Stage-specific промпты
│   ├── database/
│   │   ├── models.py           # 4 новые таблицы
│   │   └── context.py
│   ├── knowledge/
│   │   ├── faq_loader.py
│   │   └── search.py
│   ├── utils/
│   │   ├── loading_indicator.py
│   │   └── ...
│   └── main.py
├── data/
│   ├── faq.json                # База знаний (+ privacy/refund/support)
│   └── tickets/                # Экспорт тикетов для CRM
├── storage/
│   └── bot.db                  # SQLite (users, messages, tickets, events, slots)
├── README.md                   # Этот файл
├── QUALITY_STANDARD.md         # Полное описание стандарта
├── OLLAMA_SETUP.md             # Установка Ollama
└── requirements.txt
```

## 🎯 Кастомизация под вашу нишу

### Что нужно изменить:

1. **`data/faq.json`** - ваша компания, услуги, FAQ
2. **`src/funnel/offer.py`** - логика формирования предложений
3. **`src/funnel/closing.py`** - интеграция с вашей системой заказов

### Что НЕ нужно трогать:

- NLU (intent classifier, slot extractor)
- Handoff система
- Compliance модуль
- Метрики и QA

**Минимальная кастомизация = 15 минут работы с `faq.json`.**

## 📊 Метрики

### Целевые значения

| Метрика            | Целевое значение |
|--------------------|------------------|
| FRT P50            | < 20 сек         |
| FRT P90            | < 120 сек        |
| Containment Rate   | > 40%            |
| FCR                | > 70%            |
| CSAT               | > 85%            |

### Отчёты

```python
from src.metrics.calculator import MetricsCalculator

calculator = MetricsCalculator(db_path)
report = await calculator.get_weekly_report()

# Output:
# {
#   "period": "2026-W07",
#   "frt_p50_seconds": 16.0,
#   "containment_rate": 0.38,
#   "handoff_rate": 0.48,
# }
```

## 🧪 Тестирование

### Ручное тестирование

Используйте тест-кейсы из [`src/qa/test_cases.py`](src/qa/test_cases.py):

- **TC001**: "Сколько стоит?" → Запрос уточнения
- **TC002**: "Хочу вернуть заказ 12345" → Создание refund тикета
- **TC003**: "Удалите мои данные" → Создание privacy тикета
- **TC004**: "Вы мошенники" → Деэскалация + тикет
- **TC005**: "Дайте телефон клиента Иванова" → Отказ (конфиденциальность)

### Автоматическое тестирование

TODO: Test runner (roadmap Фаза 4).

## 📝 Команды бота

- `/start` - Начать диалог
- `/reset` - Очистить историю
- `/menu` - Показать меню
- `/privacy` - Управление персональными данными
- `/delete_data` - Удалить историю диалогов

## 🔒 Compliance (GDPR/152-ФЗ)

### Реализовано:

- ✅ **Privacy by design**: минимизация PII
- ✅ **Прозрачность**: уведомление о сборе данных
- ✅ **Права субъекта**: delete, export, correct data
- ✅ **Retention policy**: 7-1095 дней по цели обработки
- ✅ **Consent tracking**: история согласий

### Команды:

```
/privacy - Управление данными
  1. Удалить историю диалогов
  2. Выгрузить данные (запрос к менеджеру)
  3. Связаться по вопросам данных
```

## 🎨 Примеры диалогов

### Сценарий 1: Привлечение + Квалификация + Оффер

```
User: Привет
Bot: Привет! На связи помощник Ваша Компания 🙂
     Чем помочь: услуги/цены/сроки/контакты/поддержка?

User: Хочу узнать про разработку
Bot: Понял. 2 уточнения: какая цель и на какой срок?

User: Нужен сайт, срок - 3 недели, бюджет до 100к
Bot: Понял:
     • Задача: разработка сайта
     • Бюджет: 100000 руб
     • Срок: 3 недели
     
     Сейчас подберу варианты...
     
     Вижу 2 подходящих варианта:
     
     Вариант A — Разработка решения
     • Полный цикл разработки
     • Цена: от 50 000 руб
     • Срок: от 2 недель
     
     Какой ближе?

User: Давайте A
Bot: Отлично! Оформляем заказ.
     Оставьте контакт для связи (телефон или email).

User: +79991234567
Bot: ✅ Заявка принята!
     
     Ваши данные:
     • Задача: разработка сайта
     • Бюджет: 100000 руб
     • Срок: 3 недели
     • Контакт: +79991234567
     
     Менеджер свяжется с вами в течение часа.
```

### Сценарий 2: Privacy Request

```
User: Удалите мои данные
Bot: Я зарегистрирую ваш запрос на удаление данных.
     Для верификации личности и выполнения запроса с вами
     свяжется специалист. Ожидаемый срок ответа - до 30 дней
     (в соответствии с законом о персональных данных).
```

### Сценарий 3: Refund/Complaint

```
User: Хочу вернуть заказ 555, не подошло
Bot: Понял. Помогу оформить возврат.
     
     Уточните:
     • Номер заказа: 555 ✓
     • Причина: не подошло ✓
     • Контакт для связи
     
     Ответ по решению — до 7 рабочих дней.
```

## 📚 Документация

- [`QUALITY_STANDARD.md`](QUALITY_STANDARD.md) - Полное описание стандарта
- [`OLLAMA_SETUP.md`](OLLAMA_SETUP.md) - Установка Ollama
- [`src/qa/test_cases.py`](src/qa/test_cases.py) - Тест-кейсы

## 🛠 Roadmap

### Фаза 1-3: ✅ Реализовано

- NLU + Slot Extraction
- Воронка (7 этапов)
- Handoff + Compliance
- Метрики + QA

### Фаза 4: Production-ready (TODO)

- Funnel context в БД (Redis/SQLite)
- Полная CRM интеграция (API)
- CSAT опросы after resolution
- Web dashboard для метрик
- Автоматический test runner

### Фаза 5: Advanced (Future)

- A/B тестирование промптов
- Sentiment analysis
- Voice of Customer (VoC) analysis
- Predictive lead scoring
- Multi-channel (WhatsApp, Web widget)

## 🤝 Contributing

При добавлении новых фич:

1. Следуйте **универсальному стандарту качества** ([`QUALITY_STANDARD.md`](QUALITY_STANDARD.md))
2. Добавьте тест-кейсы в [`src/qa/test_cases.py`](src/qa/test_cases.py)
3. Обновите метрики если нужно
4. Проверьте compliance (GDPR/152-ФЗ)

## 📄 Лицензия

MIT (или ваша лицензия)

## 📞 Контакты

- Вопросы по реализации: см. [`QUALITY_STANDARD.md`](QUALITY_STANDARD.md)
- Баги/фичи: GitHub Issues
- Telegram: @your_contact

---

**Универсальный стандарт качества** - применим в любых нишах:
- B2B услуги
- E-commerce
- SaaS
- Маркетинг/лидогенерация
- Офлайн сервисы

**Минимальная кастомизация. Максимальное качество.**
