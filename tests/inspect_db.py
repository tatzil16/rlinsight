import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.utils.database import create_database

load_dotenv()

db = create_database()

# Get latest match
matches = db.get_recent_matches(limit=1)

if matches:
    match = matches[0]
    
    print("="*60)
    print("ALL DATABASE COLUMN NAMES:")
    print("="*60)
    # Get all column names from the dictionary keys
    column_names = list(match.keys())
    for i, col in enumerate(column_names, 1):
        print(f"{i:2}. {col}")
    
    print("\n" + "="*60)
    print("SAMPLE VALUES FOR EACH COLUMN:")
    print("="*60)
    for col in column_names:
        value = match[col]
        # Truncate long values for readability
        if col == 'stats_json':
            print(f"{col:30} = (JSON blob - see below)")
        elif isinstance(value, float):
            print(f"{col:30} = {value:.2f}")
        else:
            print(f"{col:30} = {value}")
    
    print("\n" + "="*60)
    print("STATS_JSON (Full Ballchasing Data):")
    print("="*60)
    
    # Parse the JSON string
    if match.get('stats_json'):
        full_stats = json.loads(match['stats_json'])
        print(json.dumps(full_stats, indent=2))
    