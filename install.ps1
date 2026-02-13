# Skript ustanovki zavisimostey dlya Windows PowerShell
# Installation script for Telegram FAQ Bot

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Telegram FAQ Bot - Installation" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

# Proverka Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found! Install Python 3.12+ from python.org" -ForegroundColor Red
    exit 1
}

# Sozdanie virtualnogo okruzheniya
Write-Host ""
Write-Host "[2/4] Creating virtual environment..." -ForegroundColor Cyan
if (Test-Path ".venv") {
    Write-Host "WARNING: Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Failed to create venv, continuing without it" -ForegroundColor Yellow
    }
}

# Ustanovka zavisimostey
Write-Host ""
Write-Host "[3/4] Installing dependencies..." -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Sozdanie .env fayla
Write-Host ""
Write-Host "[4/4] Configuring..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "WARNING: .env file already exists" -ForegroundColor Yellow
} else {
    Copy-Item .env.example .env
    Write-Host "OK: Created .env from .env.example" -ForegroundColor Green
    Write-Host "IMPORTANT: Edit .env and set TELEGRAM_BOT_TOKEN" -ForegroundColor Yellow
}

# Informatsiya o sleduyushchikh shagakh
Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "  Installation completed!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create bot via @BotFather in Telegram" -ForegroundColor White
Write-Host "2. Edit .env file and set TELEGRAM_BOT_TOKEN" -ForegroundColor White
Write-Host "3. Install Ollama from https://ollama.ai (optional)" -ForegroundColor White
Write-Host "4. Run: python src\main.py" -ForegroundColor White
Write-Host ""
