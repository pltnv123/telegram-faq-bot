@echo off
chcp 65001 >nul
echo ========================================
echo    Перезапуск Telegram бота
echo ========================================
echo.

echo [1/3] Останавливаем работающие процессы Python...
taskkill /F /IM python.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Процессы остановлены
) else (
    echo ℹ Процессы не найдены
)
timeout /t 2 >nul

echo.
echo [2/3] Ожидание завершения процессов...
timeout /t 3 >nul

echo.
echo [3/3] Запускаем бота...
start "" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python -m src.main"

echo.
echo ✓ Бот перезапущен в новом окне
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
