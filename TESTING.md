# Руководство по тестированию

## Установка зависимостей для тестирования

```bash
uv add --dev pytest pytest-asyncio
```

## Запуск тестов

### Запустить все тесты

```bash
uv run pytest
```

### Запустить конкретный файл

```bash
uv run pytest tests/test_text_filter.py
```

### Запустить с подробным выводом

```bash
uv run pytest -v
```

### Запустить с покрытием кода

```bash
uv add --dev pytest-cov
uv run pytest --cov=src --cov-report=html
```

## Структура тестов

```
tests/
├── __init__.py
├── test_text_filter.py    # Тесты фильтрации текста
├── test_search.py          # Тесты поиска по FAQ
└── test_config_loader.py   # Тесты загрузки конфигурации
```

## Написание новых тестов

### Пример базового теста

```python
from __future__ import annotations

import pytest

def test_example():
    """Описание теста."""
    result = some_function()
    assert result == expected_value
```

### Пример асинхронного теста

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Тест асинхронной функции."""
    result = await async_function()
    assert result is not None
```

## Рекомендации

1. **Покрывайте критические функции тестами** - особенно функции обработки данных и бизнес-логики
2. **Используйте понятные имена** - `test_function_name_expected_behavior`
3. **Один тест - одна проверка** - не перегружайте тесты множественными assert
4. **Используйте фикстуры** для повторяющихся настроек
5. **Изолируйте тесты** - каждый тест должен работать независимо

## Непрерывная интеграция

Добавьте в `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --dev
      - name: Run tests
        run: uv run pytest
```
