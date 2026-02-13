@echo off
chcp 65001 > nul
echo ======================================
echo   Starting Telegram FAQ Bot
echo ======================================
echo.

if not exist .env (
    echo ERROR: .env file not found!
    echo Create .env from .env.example
    pause
    exit /b 1
)

if not exist data\faq.json (
    echo ERROR: data\faq.json not found!
    pause
    exit /b 1
)

echo Starting bot... (Press Ctrl+C to stop)
echo.

python src\main.py

pause
