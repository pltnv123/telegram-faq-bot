# AI-Powered Telegram Bot with Universal Quality Standard

Professional Telegram bot powered by LLM (Ollama), implementing a **universal quality standard** for customer chatbots, applicable to any niche with minimal customization.

## 🎯 Features

### Core Capabilities
- ✅ **Complete Sales Funnel** (7 stages): Acquisition → Qualification → Offer → Closing → Support → Complaints → Retention
- ✅ **AI Generation** powered by Ollama (llama3.2:3b or mistral:7b)
- ✅ **Smart FAQ search** with quick response for simple questions
- ✅ **Sales Strategies**: SPIN, lead scoring, adaptive CTAs
- ✅ **Loading indicator** (progressive) during generation
- ✅ **Natural dialogue** with context retention
- ✅ **Beautiful minimalist UI** with purple progress dots

### NLU (Natural Language Understanding)
- ✅ **Intent Classification** with prioritization (7 groups)
- ✅ **Slot Extraction** for structured data collection
- ✅ **Confidence scoring** and disambiguation

### Handoff & Ticketing
- ✅ **Automatic escalation** for super-priority intents
- ✅ **Ticket management** with SLA tracking
- ✅ **JSON export** for CRM integration
- ✅ **Escalation rules** (security, privacy, complaints)

### Compliance
- ✅ **GDPR/Russian 152-FZ** basic implementation
- ✅ **Privacy requests** (delete, export, correct data)
- ✅ **Data minimization** (PII collection only when necessary)
- ✅ **Consent tracking**
- ✅ **`/privacy` command** for data management

### Metrics & QA
- ✅ **Event telemetry** (conversation_started, intent_classified, etc.)
- ✅ **Metrics**: FRT (P50/P90), Containment Rate, FCR
- ✅ **QA standards**: 10-point scorecard
- ✅ **Test cases** for regression (60-120 cases)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or use install script
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Setup Ollama (optional, but recommended)

```bash
# Download Ollama from https://ollama.com/download
# Install and run the model
ollama pull llama3.2:3b
ollama serve
```

See details: [`OLLAMA_SETUP.md`](OLLAMA_SETUP.md)

### 3. Configure `.env`

```bash
# Create .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
AI_TEMPERATURE=0.5
AI_MAX_TOKENS=300
```

### 4. Run the Bot

```bash
python -m src.main
```

## 📁 Project Structure

```
c:\BOT\
├── src/
│   ├── ai/                    # AI module (Ollama integration)
│   │   ├── ollama_client.py   # Streaming generation
│   │   └── prompts.py         # Optimized prompts
│   ├── bot/handlers/          # Message handlers
│   │   ├── chat.py            # Main chat handler
│   │   ├── start.py           # /start command
│   │   └── menu.py            # Menu handler
│   ├── database/              # Database layer
│   │   ├── models.py          # Data models
│   │   └── context.py         # Conversation context
│   ├── knowledge/             # Knowledge base
│   │   ├── faq_loader.py      # FAQ loader
│   │   └── search.py          # FAQ search
│   ├── utils/                 # Utilities
│   │   ├── text_filter.py     # Text cleaning
│   │   ├── intent_detection.py
│   │   └── loading_indicator.py
│   └── main.py                # Entry point
├── data/
│   └── faq.json               # FAQ database (66 items)
├── storage/
│   └── bot.db                 # SQLite database
├── README.md                  # Russian version
├── README_EN.md               # This file (English)
├── QUICKSTART.md              # Russian quick start
├── QUICKSTART_EN.md           # English quick start
└── requirements.txt
```

## 🎯 Customization for Your Niche

### What to Change:

1. **`data/faq.json`** - your company, services, FAQ
2. **`src/ai/prompts.py`** - adjust prompts for your domain
3. **`.env`** - company name, contact information

### What NOT to Touch:

- AI client (streaming, context)
- Text filtering system
- Database layer
- Progress indicator

**Minimal customization = 15 minutes working with `faq.json`.**

## 📊 Features Highlights

### 1. Beautiful Loading Animation

```
🔄 Generating...
🟣🟣🟣🟣🟣⚪⚪⚪⚪⚪ 45%
```

- Purple progress dots
- Real-time progress tracking
- Smooth spinner animation
- Shows instant result after completion

### 2. Smart Text Formatting

- Automatic line breaks after sentences
- Clean Russian text (English words filtered out)
- Proper emoji usage (2-3 per message maximum)
- Natural conversational style

### 3. Context-Aware Responses

- Remembers last 5 messages
- Direct answers to follow-up questions
- Manager contacts provided immediately when asked
- No unnecessary menu offers

## 📝 Bot Commands

- `/start` - Start conversation
- `/reset` - Clear history
- `/menu` - Show menu
- `/privacy` - Manage personal data
- `/delete_data` - Delete conversation history
- `/stats` - Show user statistics

## 🎨 Example Dialogues

### Scenario 1: Service Inquiry

```
User: Hello

Bot: Hi! ⭐
I'm here to help with our services.
What can I assist you with?

User: What services do you offer?

Bot: We provide three main services:
• Consultations (from 5000 RUB)
• Custom solutions (from 50000 RUB)
• Technical support (from 20000 RUB/month)
```

### Scenario 2: Manager Contact

```
User: Who can I discuss details with?

Bot: Our manager! 📞
Contact via:
📞 Phone: +7 (999) 123-45-67
📧 Email: info@example.com
💬 Telegram: @manager_username
```

## 🛠 Technical Stack

- **Python 3.12+**
- **aiogram 3.x** - Telegram Bot framework
- **Ollama** - Local LLM (llama3.2:3b)
- **SQLite + aiosqlite** - Database
- **aiohttp** - HTTP client for streaming
- **python-dotenv** - Environment variables

## 📊 Target Metrics

| Metric            | Target Value     |
|-------------------|------------------|
| FRT P50           | < 20 sec         |
| FRT P90           | < 120 sec        |
| Containment Rate  | > 40%            |
| FCR               | > 70%            |
| CSAT              | > 85%            |

## 🔒 Compliance (GDPR/152-FZ)

### Implemented:

- ✅ **Privacy by design**: PII minimization
- ✅ **Transparency**: data collection notification
- ✅ **Subject rights**: delete, export, correct data
- ✅ **Retention policy**: 7-1095 days by purpose
- ✅ **Consent tracking**: consent history

### Commands:

```
/privacy - Data management
  1. Delete conversation history
  2. Export data (request to manager)
  3. Contact regarding data questions
```

## 📚 Documentation

- [`README_EN.md`](README_EN.md) - This file (English)
- [`README.md`](README.md) - Russian version
- [`QUICKSTART_EN.md`](QUICKSTART_EN.md) - Quick start (English)
- [`QUICKSTART.md`](QUICKSTART.md) - Quick start (Russian)
- [`OLLAMA_SETUP.md`](OLLAMA_SETUP.md) - Ollama installation

## 🤝 Contributing

When adding new features:

1. Follow the **universal quality standard** ([`QUALITY_STANDARD.md`](QUALITY_STANDARD.md))
2. Add test cases
3. Update metrics if needed
4. Check compliance (GDPR/152-FZ)

## 📄 License

MIT

## 📞 Contact

- Implementation questions: see documentation
- Bugs/features: GitHub Issues
- Telegram: @your_contact

---

**Universal Quality Standard** - applicable to any niche:
- B2B services
- E-commerce
- SaaS
- Marketing/lead generation
- Offline services

**Minimal customization. Maximum quality.**
