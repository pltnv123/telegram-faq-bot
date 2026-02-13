"""Тестовый скрипт для проверки правильности установки."""

from __future__ import annotations

import sys
from pathlib import Path


def test_imports() -> bool:
    """Проверить что все модули импортируются."""
    print("🧪 Тестирование импортов...")

    try:
        import aiogram

        print(f"  ✅ aiogram {aiogram.__version__}")
    except ImportError as e:
        print(f"  ❌ aiogram не установлен: {e}")
        return False

    try:
        import aiohttp

        print(f"  ✅ aiohttp {aiohttp.__version__}")
    except ImportError as e:
        print(f"  ❌ aiohttp не установлен: {e}")
        return False

    try:
        import aiosqlite

        print(f"  ✅ aiosqlite {aiosqlite.__version__}")
    except ImportError as e:
        print(f"  ❌ aiosqlite не установлен: {e}")
        return False

    try:
        import dotenv

        print(f"  ✅ python-dotenv {dotenv.__version__}")
    except ImportError as e:
        print(f"  ❌ python-dotenv не установлен: {e}")
        return False

    try:
        import beartype

        print(f"  ✅ beartype {beartype.__version__}")
    except ImportError as e:
        print(f"  ❌ beartype не установлен: {e}")
        return False

    return True


def test_project_structure() -> bool:
    """Проверить что все необходимые файлы существуют."""
    print("\n📁 Проверка структуры проекта...")

    required_files = [
        "src/main.py",
        "src/config.py",
        "src/bot/keyboards.py",
        "src/bot/handlers/start.py",
        "src/bot/handlers/menu.py",
        "src/bot/handlers/chat.py",
        "src/ai/ollama_client.py",
        "src/ai/prompts.py",
        "src/knowledge/faq_loader.py",
        "src/knowledge/search.py",
        "src/database/models.py",
        "src/database/context.py",
        "data/faq.json",
        ".env.example",
        "pyproject.toml",
        "requirements.txt",
    ]

    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} не найден")
            all_exist = False

    return all_exist


def test_config() -> bool:
    """Проверить конфигурацию."""
    print("\n⚙️ Проверка конфигурации...")

    env_path = Path(".env")
    if not env_path.exists():
        print("  ⚠️ Файл .env не найден (создайте из .env.example)")
        return False

    print("  ✅ Файл .env существует")

    # Проверить что токен установлен
    with open(env_path, encoding="utf-8") as f:
        content = f.read()

    if "123456:ABC-DEF" in content:
        print("  ⚠️ TELEGRAM_BOT_TOKEN не изменен (используется пример)")
        return False

    print("  ✅ TELEGRAM_BOT_TOKEN установлен")
    return True


def main() -> None:
    """Запустить все тесты."""
    print("=" * 60)
    print("  Проверка установки Telegram FAQ Bot")
    print("=" * 60)
    print()

    success = True

    # Тест 1: Импорты
    if not test_imports():
        success = False
        print("\n❌ Некоторые зависимости не установлены")
        print("   Выполните: pip install -r requirements.txt")

    # Тест 2: Структура проекта
    if not test_project_structure():
        success = False
        print("\n❌ Некоторые файлы отсутствуют")

    # Тест 3: Конфигурация
    config_ok = test_config()

    print("\n" + "=" * 60)
    if success and config_ok:
        print("✅ Все проверки пройдены! Бот готов к запуску.")
        print("\nЗапустите бота: python src\\main.py")
    elif success:
        print("⚠️ Установка завершена, но требуется настройка:")
        print("   1. Создайте .env файл из .env.example")
        print("   2. Укажите TELEGRAM_BOT_TOKEN от @BotFather")
        print("   3. Запустите бота: python src\\main.py")
    else:
        print("❌ Обнаружены проблемы. Исправьте их перед запуском.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        sys.exit(1)
