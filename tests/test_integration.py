import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import asyncio
from src.utils.database import create_database
from src.analysis.analyzer import create_analyzer
from src.discord_bot.bot import create_bot

load_dotenv()

print("🧪 Integration Test: Database → LLM → Discord\n")

async def test_full_pipeline():
    """Test the complete pipeline with real data."""
    
    # 1. Get a match from database
    print("1️⃣ Fetching match from database...")
    db = create_database()
    matches = db.get_recent_matches(limit=1)
    
    if not matches:
        print("❌ No matches in database. Run tests/test_database.py first!")
        db.close()
        return
    
    match = matches[0]
    print(f"   ✅ Found match: {match['playlist']} ({match['result']})\n")
    
    # 2. Prepare data
    print("2️⃣ Preparing match data...")
    current_stats = {
        'goals': match['goals'],
        'assists': match['assists'],
        'saves': match['saves'],
        'shots': match['shots'],
        'shooting_percentage': match['shooting_percentage'],
        'score': match['score'],
        'avg_boost': match['avg_boost'],
        'percent_zero_boost': match['percent_zero_boost'],
        'percent_full_boost': match['percent_full_boost'],
        'amount_collected': match['amount_collected'],
        'percent_defensive_third': match['percent_defensive_third'],
        'percent_neutral_third': match['percent_neutral_third'],
        'percent_offensive_third': match['percent_offensive_third'],
        'time_behind_ball': match['time_behind_ball'],
        'avg_speed': match['avg_speed'],
        'time_supersonic': match['time_supersonic'],
        'percent_ground': match['percent_ground'],
        'percent_low_air': match['percent_low_air'],
        'percent_high_air': match['percent_high_air'],
    }
    
    match_info = {
        'playlist': match['playlist'],
        'result': match['result'],
        'duration': match['duration']
    }
    
    win_loss_data = db.get_win_loss_averages(last_n_matches=20)
    print(f"   ✅ Historical data: {win_loss_data['total_wins']} wins, {win_loss_data['total_losses']} losses\n")
    
    # 3. Generate LLM feedback
    print("3️⃣ Generating feedback with GPT-5-mini...")
    analyzer = create_analyzer()
    feedback = analyzer.analyze_match(current_stats, win_loss_data, match_info)
    print(f"   ✅ Feedback generated ({len(feedback)} characters)\n")
    
    # 4. Format for Discord
    print("4️⃣ Formatting Discord message...")
    discord_message = analyzer.format_discord_message(feedback, match_info, current_stats)
    print("   ✅ Message formatted\n")
    
    print("="*60)
    print("PREVIEW OF MESSAGE TO BE POSTED:")
    print("="*60)
    print(discord_message)
    print("="*60 + "\n")
    
    # 5. Start Discord bot
    print("5️⃣ Starting Discord bot...")
    bot = create_bot()
    bot_task = asyncio.create_task(bot.start())
    
    # Wait for bot to be ready
    max_wait = 10
    waited = 0
    while not bot.target_channel and waited < max_wait:
        await asyncio.sleep(1)
        waited += 1
    
    if not bot.target_channel:
        print("   ❌ Bot failed to connect")
        db.close()
        return
    
    print(f"   ✅ Bot connected to #{bot.channel_name}\n")
    
    # 6. Post to Discord
    print("6️⃣ Posting to Discord...")
    await bot.post_report(discord_message)
    print("   ✅ Posted!\n")
    
    # Give it time to send
    await asyncio.sleep(2)
    
    # Cleanup
    print("7️⃣ Cleaning up...")
    db.close()
    await bot.close()
    bot_task.cancel()
    
    print("\n" + "="*60)
    print("✅ INTEGRATION TEST COMPLETE!")
    print("Check your Discord #coach-feedback channel for the message.")
    print("="*60)

# Run the test
asyncio.run(test_full_pipeline())