# Quick Start Guide (English)

Get your AI Telegram bot up and running in 5 minutes!

## Prerequisites

- Python 3.12 or higher
- Telegram account
- Ollama (optional, but recommended for AI features)

## Step 1: Get Telegram Bot Token

1. Open Telegram and find `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token (looks like: `123456:ABC-DEF1234ghIkl...`)

## Step 2: Install Ollama (Optional)

### Windows

1. Download from https://ollama.com/download
2. Run the installer
3. Open terminal and run:
```bash
ollama pull llama3.2:3b
ollama serve
```

### Linux/Mac

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:3b
ollama serve
```

**Note**: Ollama will use ~2GB RAM and provides the best AI responses.

## Step 3: Setup Project

### Clone or Download

```bash
git clone <your-repo-url>
cd BOT
```

### Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Step 4: Configure Environment

Create `.env` file in project root:

```bash
# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Ollama API settings
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Database settings
DB_PATH=storage/conversations.db

# Context settings
MAX_CONTEXT_MESSAGES=5
CONTEXT_RETENTION_DAYS=7

# AI generation settings
AI_TEMPERATURE=0.5
AI_MAX_TOKENS=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Company name (for prompts)
COMPANY_NAME=Your Company
```

### Important: Replace Values

- `YOUR_BOT_TOKEN_HERE` - paste your actual token from BotFather
- `Your Company` - your company name
- Other values can be left as default

## Step 5: Customize FAQ (Optional)

Edit `data/faq.json` to add your company information:

```json
{
  "company": {
    "name": "Your Company",
    "phone": "+7 (999) 123-45-67",
    "email": "info@yourcompany.com",
    "telegram": "@your_manager"
  },
  "faq": [
    {
      "id": 1,
      "question": "What services do you offer?",
      "answer": "We provide...",
      "keywords": ["services", "what", "offer"]
    }
  ]
}
```

## Step 6: Run the Bot

```bash
python -m src.main
```

You should see:

```
2026-02-13 13:00:00 - __main__ - INFO - Starting Telegram FAQ Bot...
2026-02-13 13:00:00 - __main__ - INFO - [OK] Configuration loaded
2026-02-13 13:00:00 - __main__ - INFO - [OK] Database initialized
2026-02-13 13:00:00 - __main__ - INFO - [OK] Loaded FAQ items: 66
2026-02-13 13:00:00 - __main__ - INFO - [OK] Ollama is available (model: llama3.2:3b)
2026-02-13 13:00:00 - __main__ - INFO - [OK] Bot started and ready to receive messages!
```

## Step 7: Test Your Bot

1. Open Telegram
2. Find your bot (by username from BotFather)
3. Send `/start`
4. Try asking: "What services do you offer?"

## Features

### Beautiful Loading Animation

When generating AI responses, you'll see:

```
🔄 Generating...
🟣🟣🟣🟣🟣⚪⚪⚪⚪⚪ 45%
```

### Smart Responses

- Natural dialogue with context memory
- Automatic line breaks for readability
- Pure Russian language (English words filtered)
- Limited emoji usage (2-3 per message)

### Commands

- `/start` - Start conversation
- `/menu` - Show menu
- `/reset` - Clear conversation history
- `/stats` - Show your statistics
- `/privacy` - Manage your data

## Troubleshooting

### Bot doesn't respond

1. Check if Ollama is running: `ollama serve`
2. Check bot token in `.env`
3. Make sure Python script is running
4. Check logs in `bot.log`

### "Model not found" error

```bash
# Pull the model again
ollama pull llama3.2:3b
```

### Slow responses

1. Reduce `AI_MAX_TOKENS` in `.env` (try 200)
2. Use a smaller model: `ollama pull llama3.2:3b` instead of 7b
3. Check your internet connection

### Unicode errors in console

This is normal on Windows. The bot works fine, just console can't display some emojis.

## Next Steps

1. **Customize FAQ**: Edit `data/faq.json` with your services
2. **Adjust Prompts**: Modify `src/ai/prompts.py` for your domain
3. **Change Colors**: Edit progress bar in `src/bot/handlers/chat.py`
4. **Add More**: Expand functionality as needed

## Configuration Tips

### For Faster Responses

```bash
AI_MAX_TOKENS=200
AI_TEMPERATURE=0.5
MAX_CONTEXT_MESSAGES=3
```

### For Better Quality

```bash
AI_MAX_TOKENS=500
AI_TEMPERATURE=0.6
MAX_CONTEXT_MESSAGES=10
OLLAMA_MODEL=llama3.2:7b  # Larger model
```

### For Production

```bash
LOG_LEVEL=WARNING
CONTEXT_RETENTION_DAYS=30
AI_TEMPERATURE=0.5
```

## Development Mode

To restart bot automatically on changes, use:

```bash
# Install watchdog
pip install watchdog

# Run with auto-reload (not included by default)
# You can use: python -m watchdog.watchmedo auto-restart --patterns="*.py" --recursive python -m src.main
```

## Stopping the Bot

Press `Ctrl+C` in the terminal where bot is running.

On Windows, you can also:
```bash
taskkill /F /IM python.exe
```

## Getting Help

- Check logs in `bot.log`
- Read full documentation: [`README_EN.md`](README_EN.md)
- Ollama setup: [`OLLAMA_SETUP.md`](OLLAMA_SETUP.md)
- Russian version: [`QUICKSTART.md`](QUICKSTART.md)

---

**Congratulations! Your AI-powered Telegram bot is running! 🎉**
