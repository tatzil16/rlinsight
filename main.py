"""Main application - polls Ballchasing and posts analysis to Discord."""

import sys
from pathlib import Path
import asyncio
from dotenv import load_dotenv
import os

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.ballchasing_client import create_client
from src.utils.database import create_database
from src.analysis.analyzer import create_analyzer
from src.discord_bot.bot import create_bot

load_dotenv()

MY_STEAM_ID = os.getenv("STEAM_ID")
POLL_INTERVAL = 5  # Seconds between checks


def find_player(team_data, steam_id):
    """Find a player by Steam ID in a team."""
    players = team_data.get('players', [])
    for player in players:
        player_id = player.get('id', {})
        if player_id.get('id') == steam_id:
            return player
    return None


async def check_and_analyze_new_matches(client, db, analyzer, bot):
    """
    Check for new matches and analyze them.
    
    Returns:
        Number of new matches processed
    """
    print("🔍 Checking for new matches...")
    
    # Get latest replays
    replays = client.get_replays(uploader="me", count=5)
    
    if not replays:
        print("   No replays found")
        return 0
    
    new_matches = 0
    
    for replay in replays:
        replay_id = replay['id']
        
        # Skip if already analyzed
        if db.match_exists(replay_id):
            continue
        
        print(f"\n🆕 New match found: {replay.get('replay_title', 'Untitled')}")
        
        # Get full details
        details = client.get_replay_details(replay_id)
        
        # Find your player
        your_player = find_player(details.get('blue', {}), MY_STEAM_ID)
        team_color = 'blue'
        if not your_player:
            your_player = find_player(details.get('orange', {}), MY_STEAM_ID)
            team_color = 'orange'
        
        if not your_player:
            print(f"   ⚠️  You were not found in this match, skipping...")
            continue
        
        # Save to database
        db.save_match(replay_id, details, your_player)
        print(f"   ✅ Saved to database")
        
        # Prepare stats for analysis
        stats = your_player.get('stats', {})
        current_stats = {
            'goals': stats.get('core', {}).get('goals', 0),
            'assists': stats.get('core', {}).get('assists', 0),
            'saves': stats.get('core', {}).get('saves', 0),
            'shots': stats.get('core', {}).get('shots', 0),
            'shooting_percentage': stats.get('core', {}).get('shooting_percentage', 0),
            'score': stats.get('core', {}).get('score', 0),
            'avg_boost': stats.get('boost', {}).get('avg_amount', 0),
            'percent_zero_boost': stats.get('boost', {}).get('percent_zero_boost', 0),
            'percent_full_boost': stats.get('boost', {}).get('percent_full_boost', 0),
            'amount_collected': stats.get('boost', {}).get('amount_collected', 0),
            'percent_defensive_third': stats.get('positioning', {}).get('percent_defensive_third', 0),
            'percent_neutral_third': stats.get('positioning', {}).get('percent_neutral_third', 0),
            'percent_offensive_third': stats.get('positioning', {}).get('percent_offensive_third', 0),
            'time_behind_ball': stats.get('positioning', {}).get('time_behind_ball', 0),
            'avg_speed': stats.get('movement', {}).get('avg_speed', 0),
            'time_supersonic': stats.get('movement', {}).get('time_supersonic_speed', 0),
            'percent_ground': stats.get('movement', {}).get('percent_ground', 0),
            'percent_low_air': stats.get('movement', {}).get('percent_low_air', 0),
            'percent_high_air': stats.get('movement', {}).get('percent_high_air', 0),
        }
        
        # Determine result
        blue_goals = details.get('blue', {}).get('stats', {}).get('core', {}).get('goals', 0)
        orange_goals = details.get('orange', {}).get('stats', {}).get('core', {}).get('goals', 0)
        result = 'win' if (team_color == 'blue' and blue_goals > orange_goals) or (team_color == 'orange' and orange_goals > blue_goals) else 'loss'
        
        match_info = {
            'playlist': details.get('playlist_name', 'Unknown'),
            'result': result,
            'duration': details.get('duration', 0)
        }
        
        # Get win/loss averages
        win_loss_data = db.get_win_loss_averages(last_n_matches=20)
        
        # Generate feedback
        print(f"   🤖 Analyzing with GPT-5-mini...")
        feedback = analyzer.analyze_match(current_stats, win_loss_data, match_info)
        
        # Format and post to Discord
        discord_message = analyzer.format_discord_message(feedback, match_info, current_stats)
        print(f"   📤 Posting to Discord...")
        await bot.post_report(discord_message)
        
        print(f"   ✅ Complete!\n")
        new_matches += 1
    
    return new_matches


async def main():
    """Main application loop."""
    print("🚀 GameInsight - Rocket League Match Analyzer")
    print("="*60)
    print(f"Steam ID: {MY_STEAM_ID}")
    print(f"Poll interval: {POLL_INTERVAL} seconds")
    print("="*60 + "\n")
    
    # Initialize components
    print("Initializing components...")
    client = create_client()
    db = create_database()
    analyzer = create_analyzer()
    bot = create_bot()
    
    # Start Discord bot
    print("Starting Discord bot...")
    bot_task = asyncio.create_task(bot.start())
    
    # Wait for bot to be ready
    max_wait = 10
    waited = 0
    while not bot.target_channel and waited < max_wait:
        await asyncio.sleep(1)
        waited += 1
    
    if not bot.target_channel:
        print("❌ Failed to connect Discord bot. Exiting.")
        db.close()
        return
    
    print(f"✅ Discord bot ready in #{bot.channel_name}\n")
    
    # Main polling loop
    try:
        while True:
            try:
                new_matches = await check_and_analyze_new_matches(client, db, analyzer, bot)
                
                if new_matches == 0:
                    print(f"   No new matches (checking again in {POLL_INTERVAL}s)")
                else:
                    print(f"✅ Processed {new_matches} new match(es)")
                
                print()
                await asyncio.sleep(POLL_INTERVAL)
                
            except KeyboardInterrupt:
                raise  # Re-raise to exit cleanly
            except Exception as e:
                print(f"❌ Error in polling loop: {e}")
                import traceback
                traceback.print_exc()
                print(f"\nRetrying in {POLL_INTERVAL}s...\n")
                await asyncio.sleep(POLL_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down...")
    
    finally:
        # Clean up
        print("Closing connections...")
        db.close()
        await bot.close()
        bot_task.cancel()
        print("✅ Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())