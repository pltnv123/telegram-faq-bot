@echo off
chcp 65001 > nul
echo ======================================
echo   Telegram FAQ Bot - Installation
echo ======================================
echo.

echo [1/3] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Creating .env file...
if exist .env (
    echo WARNING: .env already exists
) else (
    copy .env.example .env
    echo OK: .env created from .env.example
)

echo.
echo [3/3] Creating folders...
if not exist storage mkdir storage

echo.
echo ======================================
echo   Installation completed!
echo ======================================
echo.
echo Next steps:
echo 1. Edit .env and set TELEGRAM_BOT_TOKEN
echo 2. Edit data\faq.json with your info
echo 3. Run: python src\main.py
echo.
pause
