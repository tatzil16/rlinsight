# GameInsight - Rocket League Match Analyzer

Automated post-match analysis for Rocket League using AI coaching feedback.

## Features

- 🎮 Automatically fetches matches from Ballchasing API
- 🧠 Analyzes performance using GPT-5-mini with win/loss pattern recognition
- 📊 Tracks historical stats in SQLite database
- 💬 Posts coaching feedback to Discord with player mentions

## Setup

### 1. Prerequisites

- Python 3.10+
- Ballchasing account with API key
- OpenAI API key
- Discord bot token

### 2. Installation
```bash
# Clone repository
git clone <your-repo-url>
cd rlinsight

# Create virtual environment
conda create -n rlinsight-mcp python=3.11
conda activate rlinsight-mcp

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the project root:
```
BALLCHASING_API_KEY=your_ballchasing_key
OPENAI_API_KEY=your_openai_key
DISCORD_BOT_TOKEN=your_discord_token
STEAM_ID=your_steam_id
DISCORD_MENTION_USER=YourDiscordUsername
```

### 4. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Enable these Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent
5. Copy the bot token to your `.env` file
6. Invite bot to your server using OAuth2 URL Generator

### 5. Initial Data Population
```bash
# Populate database with your match history
python tests/test_database.py
```

## Usage

### Run the main application:
```bash
python main.py
```

The bot will:
- Poll Ballchasing every 60 seconds for new matches
- Analyze your performance compared to win/loss patterns
- Post coaching feedback to Discord

### Testing
```bash
# Test individual components
python tests/test_ballchasing.py
python tests/test_database.py
python tests/test_analyzer.py
python tests/test_discord.py

# Test full integration
python tests/test_integration.py
```

## Project Structure
```
rlinsight/
├── src/
│   ├── analysis/          # LLM coaching analysis
│   │   ├── analyzer.py
│   │   └── prompts.py
│   ├── discord_bot/       # Discord integration
│   │   └── bot.py
│   └── utils/             # Core utilities
│       ├── ballchasing_client.py
│       └── database.py
├── tests/                 # Test scripts
├── main.py               # Main application entry point
├── requirements.txt
└── .env                  # Configuration (not in git)
```

## How It Works

1. **Match Detection**: Polls Ballchasing API for new replays
2. **Data Extraction**: Parses player stats (boost, positioning, shooting, etc.)
3. **Pattern Analysis**: Compares current match to historical win/loss averages
4. **LLM Coaching**: GPT-5-mini generates actionable feedback based on patterns
5. **Discord Notification**: Posts formatted report with @mention

## Tech Stack

- **Ballchasing API** - Match data
- **OpenAI GPT-5-mini** - Coaching analysis
- **SQLite** - Match history storage
- **Discord.py** - Bot integration
- **Python asyncio** - Concurrent operations

## License

MIT