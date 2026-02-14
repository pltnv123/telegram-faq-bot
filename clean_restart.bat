@echo off
chcp 65001 >nul
echo ========================================
echo    Полная очистка и перезапуск бота
echo ========================================
echo.

echo [1/5] Останавливаем все процессы Python...
taskkill /F /IM python.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Процессы остановлены
) else (
    echo ℹ Процессы не найдены
)
timeout /t 2 >nul

echo.
echo [2/5] Удаляем кэш Python (__pycache__)...
for /d /r "%~dp0" %%d in (__pycache__) do (
    if exist "%%d" (
        echo Удаляем: %%d
        rd /s /q "%%d" 2>nul
    )
)
echo ✓ Кэш очищен

echo.
echo [3/5] Удаляем скомпилированные .pyc файлы...
del /s /q "%~dp0\*.pyc" 2>nul
echo ✓ Файлы .pyc удалены

echo.
echo [4/5] Ожидание завершения всех процессов...
timeout /t 5 >nul

echo.
echo [5/5] Запускаем бота с чистым кэшом...
start "" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python -m src.main"

echo.
echo ========================================
echo ✓ Бот перезапущен с обновленным кодом!
echo ========================================
echo.
echo Теперь все кнопки должны быть на русском.
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
