"""MCP tools for querying Rocket League match data."""

import os
import json
from typing import Dict, List, Optional
from src.utils.database import create_database

# Your Steam ID from environment
STEAM_ID = os.getenv("STEAM_ID")


def get_latest_match() -> Dict:
    """
    Get the most recent Rocket League match.
    
    Returns:
        Dictionary with match details including stats
    """
    db = create_database()
    matches = db.get_recent_matches(limit=1)
    db.close()
    
    if not matches:
        return {"error": "No matches found in database"}
    
    return matches[0]


def get_win_loss_comparison(last_n_matches: int = 10) -> Dict:
    """
    Get comparison of stats between wins and losses.
    
    Args:
        last_n_matches: Number of recent matches to analyze
        
    Returns:
        Dictionary with 'wins' and 'losses' stat averages
    """
    db = create_database()
    data = db.get_win_loss_averages(last_n_matches=last_n_matches)
    db.close()
    
    return data


def query_matches(
    result: Optional[str] = None,
    min_goals: Optional[int] = None,
    max_goals: Optional[int] = None,
    min_saves: Optional[int] = None,
    max_saves: Optional[int] = None,
    date_after: Optional[str] = None,
    date_before: Optional[str] = None,
    sort_by: str = "date",
    limit: int = 10
) -> List[Dict]:
    """
    Query matches with optional filters.
    
    Args:
        result: Filter by 'win' or 'loss'
        min_goals: Minimum goals scored
        max_goals: Maximum goals scored
        min_saves: Minimum saves made
        max_saves: Maximum saves made
        date_after: Only matches after this date (ISO format: 2024-10-01)
        date_before: Only matches before this date (ISO format: 2024-10-20)
        sort_by: Sort by 'date', 'goals', 'score', 'shooting_percentage'
        limit: Maximum number of matches to return
        
    Returns:
        List of match dictionaries
    """
    db = create_database()
    
    # Get a large pool of matches to filter from
    matches = db.get_recent_matches(limit=100)
    
    # Apply filters
    filtered = []
    for match in matches:
        # Filter by result
        if result and match.get('result') != result:
            continue
        
        # Filter by minimum goals
        if min_goals is not None and match.get('goals', 0) < min_goals:
            continue

        # Filter by maximum goals
        if max_goals is not None and match.get('goals', 0) > max_goals:
            continue
        
        # Filter by minimum saves
        if min_saves is not None and match.get('saves', 0) < min_saves:
            continue

        # Filter by maximum saves
        if max_saves is not None and match.get('saves', 0) < max_saves:
            continue
        
        # Filter by date after
        if date_after and match.get('date', '') < date_after:
            continue
        
        # Filter by date before
        if date_before and match.get('date', '') > date_before:
            continue
        
        filtered.append(match)
    
    # Sort results
    if sort_by == "date":
        filtered.sort(key=lambda m: m.get('date', ''), reverse=True)
    elif sort_by == "goals":
        filtered.sort(key=lambda m: m.get('goals', 0), reverse=True)
    elif sort_by == "score":
        filtered.sort(key=lambda m: m.get('score', 0), reverse=True)
    elif sort_by == "shooting_percentage":
        filtered.sort(key=lambda m: m.get('shooting_percentage', 0), reverse=True)
    
    db.close()
    
    # Return up to limit
    return filtered[:limit]


def get_player_averages(last_n_matches: int = 10) -> Dict:
    """
    Get average stats over recent matches.
    
    Args:
        last_n_matches: Number of recent matches to average
        
    Returns:
        Dictionary with average stats
    """
    db = create_database()
    averages = db.get_averages(last_n_matches=last_n_matches)
    db.close()
    
    return averages


def get_match_details(replay_id: str) -> Dict:
    """
    Get full details for a specific match by replay ID.
    
    Args:
        replay_id: Ballchasing replay ID
        
    Returns:
        Dictionary with full match data
    """
    db = create_database()
    match = db.get_match_by_id(replay_id)
    db.close()
    
    if not match:
        return {"error": f"Match {replay_id} not found in database"}
    
    return match