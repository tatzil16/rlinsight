import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import create_database

print("🗑️  Removing Most Recent Match from Database\n")

db = create_database()

# Get the most recent match
matches = db.get_recent_matches(limit=1)

if not matches:
    print("❌ No matches in database to remove")
    db.close()
    exit()

match = matches[0]
replay_id = match['replay_id']

print(f"Most recent match:")
print(f"  Replay ID: {replay_id}")
print(f"  Date: {match['date']}")
print(f"  Playlist: {match['playlist']}")
print(f"  Result: {match['result'].upper()}")
print(f"  Stats: {match['goals']}G / {match['assists']}A / {match['saves']}S")
print()

# Confirm deletion
confirm = input("Delete this match? (yes/no): ")

if confirm.lower() != 'yes':
    print("❌ Cancelled")
    db.close()
    exit()

# Delete the match
cursor = db.conn.cursor()
cursor.execute("DELETE FROM matches WHERE replay_id = ?", (replay_id,))
db.conn.commit()

print(f"\n✅ Deleted match {replay_id}")
print("\nYou can now run main.py and it will re-detect and analyze this match!")

# Show remaining matches
remaining = db.get_recent_matches(limit=5)
print(f"\nRemaining matches in database: {len(remaining)}")

db.close()