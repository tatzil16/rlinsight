import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import asyncio
from src.discord_bot.bot import create_bot

load_dotenv()

print("🤖 Testing Discord Bot\n")

async def test_bot():
    """Test sending a message to Discord."""
    
    # Create bot
    bot = create_bot()
    
    # Start bot in background
    print("Starting bot...")
    task = asyncio.create_task(bot.start())
    
    # Wait for bot to connect and find channel
    max_wait = 10  # Wait up to 10 seconds
    waited = 0
    while not bot.target_channel and waited < max_wait:
        await asyncio.sleep(1)
        waited += 1
        print(f"Waiting for bot to connect... ({waited}s)")
    
    if not bot.target_channel:
        print("❌ Bot failed to find channel after 10 seconds")
        await bot.close()
        task.cancel()
        return
    
    print(f"✅ Bot is ready! Found channel: #{bot.channel_name}")
    
    # Send test message
    test_message = """🎮 **GameInsight Test Report** 🏆

**Match:** Test Match | WIN
**Stats:** 3G / 2A / 1S

**Coach's Analysis:**
This is a test message from your GameInsight bot! If you can see this, the bot is working correctly. 🚀

---
_System test successful!_
"""
    
    print("Sending test message...")
    await bot.post_report(test_message)
    
    # Give it time to send
    await asyncio.sleep(2)
    
    # Close bot
    print("\nClosing bot...")
    await bot.close()
    try:
        task.cancel()
        await task
    except asyncio.CancelledError:
        pass
    
    print("✅ Test complete! Check your Discord #coach-feedback channel.")

# Run the test
asyncio.run(test_bot())