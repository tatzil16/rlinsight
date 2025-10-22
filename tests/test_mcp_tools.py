import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.mcp_server.tools import (
    get_latest_match,
    get_win_loss_comparison,
    query_matches,
    get_player_averages,
    get_match_details
)

load_dotenv()

print("🧪 Testing MCP Tools\n")

# Test 1: Get latest match
print("="*60)
print("TEST 1: get_latest_match()")
print("="*60)

latest = get_latest_match()
if "error" not in latest:
    print(f"✅ Found latest match:")
    print(f"  Playlist: {latest['playlist']}")
    print(f"  Result: {latest['result']}")
    print(f"  Stats: {latest['goals']}G / {latest['assists']}A / {latest['saves']}S")
else:
    print(f"❌ {latest['error']}")

# Test 2: Win/loss comparison
print("\n" + "="*60)
print("TEST 2: get_win_loss_comparison()")
print("="*60)

comparison = get_win_loss_comparison(last_n_matches=20)
if comparison.get('total_wins', 0) > 0 or comparison.get('total_losses', 0) > 0:
    print(f"✅ Found comparison data:")
    print(f"  Total wins: {comparison['total_wins']}")
    print(f"  Total losses: {comparison['total_losses']}")
    print(f"  Win avg boost: {comparison['wins'].get('avg_boost', 0):.1f}")
    print(f"  Loss avg boost: {comparison['losses'].get('avg_boost', 0):.1f}")
else:
    print("❌ No comparison data available")

# Test 3: Query matches
print("\n" + "="*60)
print("TEST 3: query_matches() - Multiple filters")
print("="*60)

# Test 3a: Get wins with 2+ goals
print("\nQuery: Wins with 2+ goals")
good_wins = query_matches(result='win', min_goals=2, limit=3)
if good_wins:
    print(f"✅ Found {len(good_wins)} matches:")
    for match in good_wins:
        print(f"  - {match['result'].upper()}: {match['goals']}G / {match['assists']}A / {match['saves']}S ({match['date'][:10]})")
else:
    print("❌ No matches found")

# Test 3b: Get best scoring games
print("\nQuery: Top scoring games")
best_games = query_matches(sort_by='goals', limit=3)
if best_games:
    print(f"✅ Found {len(best_games)} matches:")
    for match in best_games:
        print(f"  - {match['goals']} goals in {match['playlist']} ({match['result'].upper()})")
else:
    print("❌ No matches found")

# Test 3c: Get recent losses with high saves (defensive games)
print("\nQuery: Losses with 3+ saves (defensive games)")
defensive_losses = query_matches(result='loss', min_saves=3, limit=3)
if defensive_losses:
    print(f"✅ Found {len(defensive_losses)} matches:")
    for match in defensive_losses:
        print(f"  - {match['saves']} saves, {match['goals']}G ({match['date'][:10]})")
else:
    print("❌ No matches found")

# Test 4: Player averages
print("\n" + "="*60)
print("TEST 4: get_player_averages(last_n_matches=10)")
print("="*60)

averages = get_player_averages(last_n_matches=10)
if averages.get('match_count', 0) > 0:
    print(f"✅ Calculated averages over {averages['match_count']} matches:")
    print(f"  Avg goals: {averages['avg_goals']:.2f}")
    print(f"  Avg assists: {averages['avg_assists']:.2f}")
    print(f"  Avg boost: {averages['avg_boost']:.1f}")
else:
    print("❌ No matches to average")

# Test 5: Get match details
print("\n" + "="*60)
print("TEST 5: get_match_details(replay_id)")
print("="*60)

if not latest or "error" in latest:
    print("⏭️  Skipping (no latest match)")
else:
    replay_id = latest['replay_id']
    details = get_match_details(replay_id)
    if "error" not in details:
        print(f"✅ Found match details:")
        print(f"  Replay ID: {details['replay_id']}")
        print(f"  Playlist: {details['playlist']}")
        print(f"  Duration: {details['duration']}s")
    else:
        print(f"❌ {details['error']}")

print("\n" + "="*60)
print("✅ All tool tests complete!")
print("="*60)