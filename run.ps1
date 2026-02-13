# Run script for Telegram FAQ Bot

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Starting Telegram FAQ Bot" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Create .env from .env.example and set TELEGRAM_BOT_TOKEN" -ForegroundColor Yellow
    exit 1
}

# Check data/faq.json
if (-not (Test-Path "data\faq.json")) {
    Write-Host "ERROR: data\faq.json not found!" -ForegroundColor Red
    exit 1
}

# Start bot
Write-Host "Starting bot... (Press Ctrl+C to stop)" -ForegroundColor Cyan
Write-Host ""

python src\main.py
