import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.utils.database import create_database
from src.analysis.analyzer import create_analyzer

load_dotenv()

print("🤖 Testing LLM Match Analyzer with Win/Loss Analysis\n")

# Get a match from the database
db = create_database()
matches = db.get_recent_matches(limit=1)

if not matches:
    print("❌ No matches in database. Run tests/test_database.py first!")
    exit()

match = matches[0]
print(f"Analyzing match: {match.get('playlist')} ({match.get('result')})\n")

# Get win/loss averages (NOT regular averages!)
win_loss_data = db.get_win_loss_averages(last_n_matches=20)

print(f"📊 Historical data: {win_loss_data['total_wins']} wins, {win_loss_data['total_losses']} losses\n")

# Prepare data for analyzer
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

# Create analyzer and generate feedback
print("🔄 Calling GPT-5-mini with win/loss comparison...\n")
analyzer = create_analyzer()
feedback = analyzer.analyze_match(current_stats, win_loss_data, match_info)  # Pass win_loss_data!

print("="*60)
print("📊 RAW FEEDBACK:\n")
print(feedback)
print("\n" + "="*60)

# Format for Discord
discord_message = analyzer.format_discord_message(feedback, match_info, current_stats)
print("\n💬 DISCORD MESSAGE:\n")
print(discord_message)

db.close()