import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now imports will work
from dotenv import load_dotenv
import os
from src.utils.ballchasing_client import create_client
from src.utils.database import create_database

load_dotenv()

MY_STEAM_ID = os.getenv("STEAM_ID")

# Helper function to find player
def find_player(team_data, steam_id):
    players = team_data.get('players', [])
    for player in players:
        if player.get('id', {}).get('id') == steam_id:
            return player
    return None

# Create database
db = create_database()
print("✅ Database initialized\n")

# Fetch your latest match
client = create_client()
replays = client.get_replays(uploader="me", count=10)

print(f"Found {len(replays)} replays. Saving to database...\n")

for replay in replays:
    replay_id = replay['id']
    
    # Check if already saved
    if db.match_exists(replay_id):
        print(f"⏭️  Skipping {replay_id} (already in database)")
        continue
    
    # Get full details
    details = client.get_replay_details(replay_id)
    
    # Find your player
    your_player = find_player(details.get('blue', {}), MY_STEAM_ID)
    if not your_player:
        your_player = find_player(details.get('orange', {}), MY_STEAM_ID)
    
    if your_player:
        db.save_match(replay_id, details, your_player)
        print(f"✅ Saved match: {details.get('title', 'Untitled')}")
    else:
        print(f"❌ Could not find you in match {replay_id}")

print("\n" + "="*50)
print("DATABASE CONTENTS:\n")

# Show recent matches
recent = db.get_recent_matches(limit=5)
print(f"Recent matches: {len(recent)}\n")

for match in recent:
    print(f"• {match['playlist']} - {match['result'].upper()}")
    print(f"  Score: Goals={match['goals']}, Assists={match['assists']}, Saves={match['saves']}")
    print(f"  Boost: Avg={match['avg_boost']:.1f}, Zero={match['percent_zero_boost']:.1f}%")
    print(f"  Position: Def={match['percent_defensive_third']:.1f}%, Off={match['percent_offensive_third']:.1f}%")
    print()

# Show averages
print("="*50)
print("YOUR AVERAGES (last 10 games):\n")

averages = db.get_averages(last_n_matches=10)
if averages.get('match_count', 0) > 0:
    print(f"📊 Based on {int(averages['match_count'])} matches\n")
    
    print("CORE STATS:")
    print(f"  Goals: {averages['avg_goals']:.2f}")
    print(f"  Assists: {averages['avg_assists']:.2f}")
    print(f"  Saves: {averages['avg_saves']:.2f}")
    print(f"  Shots: {averages['avg_shots']:.2f}")
    print(f"  Shooting %: {averages['avg_shooting_pct']:.1f}%\n")
    
    print("BOOST MANAGEMENT:")
    print(f"  Avg Boost: {averages['avg_boost']:.1f}")
    print(f"  Time at Zero: {averages['avg_percent_zero_boost']:.1f}%")
    print(f"  Time at Full: {averages['avg_percent_full_boost']:.1f}%\n")
    
    print("POSITIONING:")
    print(f"  Defensive Third: {averages['avg_percent_defensive_third']:.1f}%")
    print(f"  Neutral Third: {averages['avg_percent_neutral_third']:.1f}%")
    print(f"  Offensive Third: {averages['avg_percent_offensive_third']:.1f}%")
    print(f"  Behind Ball: {averages['avg_time_behind_ball']:.1f}s\n")
    
    print("MOVEMENT:")
    print(f"  Avg Speed: {averages['avg_speed']:.0f}")
    print(f"  Time Supersonic: {averages['avg_time_supersonic']:.1f}s")
    print(f"  Ground Time: {averages['avg_percent_ground']:.1f}%")
    print(f"  Low Air: {averages['avg_percent_low_air']:.1f}%")
    print(f"  High Air: {averages['avg_percent_high_air']:.1f}%")
else:
    print("No matches in database yet")

db.close()