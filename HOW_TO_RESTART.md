# Как правильно перезапустить бота

## Проблема: Конфликт экземпляров

Если вы видите в логах:
```
TelegramConflictError: Conflict: terminated by other getUpdates request
```

Это значит где-то уже запущен другой экземпляр бота с тем же токеном.

---

## Решение

### Способ 1: Найти и закрыть окна с ботом

1. Проверьте все открытые окна PowerShell/CMD
2. Найдите то где выполняется `python -m src.main`
3. Нажмите `Ctrl+C` в этом окне
4. Подождите 5 секунд
5. Запустите бота в новом окне

### Способ 2: Убить все процессы Python (радикально)

```powershell
# Закрыть все Python процессы
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Подождать 5 секунд
Start-Sleep -Seconds 5

# Запустить бота
python -m src.main
```

### Способ 3: Перезагрузить компьютер (если ничего не помогает)

Иногда процесс может зависнуть в фоне. Перезагрузка решит проблему.

---

## Правильный запуск бота

### Шаг 1: Убедитесь что бот не запущен

```powershell
# Проверить запущенные процессы Python
Get-Process python -ErrorAction SilentlyContinue
```

Если видите процессы - остановите их (см. Способ 2 выше).

### Шаг 2: Перейти в папку проекта

```powershell
cd c:\BOT
```

### Шаг 3: Запустить бота

```powershell
python -m src.main
```

### Шаг 4: Проверить логи

Вы должны увидеть:
```
[OK] Configuration loaded
[OK] Database initialized
[OK] Loaded FAQ items: 8
[OK] Loaded services: 3
[WARNING] Ollama is not available...
[OK] Handlers registered
[OK] Bot started and ready to receive messages!
```

Если видите "Conflict" - вернитесь к Шагу 1.

---

## Быстрый запуск через скрипт

```powershell
.\run_simple.bat
```

Или через PowerShell:
```powershell
.\run.ps1
```

---

## Остановка бота

**В том же окне где запущен:**
- Нажмите `Ctrl+C`
- Подождите пока бот корректно завершится
- Вы увидите: `[STOP] Bot stopped`

**Из другого окна:**
```powershell
Get-Process python | Where-Object {$_.CommandLine -like '*src.main*'} | Stop-Process
```

---

## Проверка что бот работает

### В консоли:
Должны быть логи без ошибок "Conflict"

### В Telegram:
1. Откройте вашего бота
2. Отправьте `/start`
3. Если получили ответ - бот работает!

---

## Если все еще не работает

1. **Проверьте токен** в `.env` файле
2. **Проверьте интернет** соединение
3. **Перезагрузите** компьютер
4. **Создайте нового бота** через @BotFather (новый токен)

---

**Текущий статус:** Бот запущен с PID 25148

Если конфликт продолжается - просто подождите 1-2 минуты, Telegram автоматически отключит старый экземпляр.
