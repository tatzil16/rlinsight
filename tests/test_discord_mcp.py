import sys
from pathlib import Path
import asyncio

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.discord_bot.bot import create_bot

load_dotenv()

print("🤖 Testing Discord Bot with MCP Integration\n")
print("Instructions:")
print("1. The bot will start and connect to Discord")
print("2. Go to your #coach-feedback channel")
print("3. Type: @GameInsight Why did I lose my last game?")
print("4. Watch the bot respond!")
print("5. Press Ctrl+C to stop\n")

async def test_bot():
    """Run the bot and wait for messages."""
    bot = create_bot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping bot...")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(test_bot())