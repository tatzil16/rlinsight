import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class MatchDatabase:
    """Database for storing and retrieving Rocket League match history."""
    
    def __init__(self, db_path: str = "data/matches.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self._create_tables()
    
    def _create_tables(self):
        """Create the matches table if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                replay_id TEXT PRIMARY KEY,
                date TIMESTAMP,
                duration INTEGER,
                playlist TEXT,
                result TEXT,
                team_color TEXT,
                
                -- Core stats
                goals INTEGER,
                assists INTEGER,
                saves INTEGER,
                shots INTEGER,
                score INTEGER,
                shooting_percentage REAL,
                
                -- Key boost metrics
                avg_boost REAL,
                percent_zero_boost REAL,
                percent_full_boost REAL,
                amount_collected INTEGER,
                amount_stolen INTEGER,
                
                -- Key movement metrics
                avg_speed INTEGER,
                time_supersonic REAL,
                percent_ground REAL,
                percent_low_air REAL,
                percent_high_air REAL,
                
                -- Key positioning metrics
                percent_defensive_third REAL,
                percent_offensive_third REAL,
                percent_neutral_third REAL,
                time_behind_ball REAL,
                time_infront_ball REAL,
                
                -- Metadata
                analyzed_at TIMESTAMP,
                stats_json TEXT
            )
        """)
        self.conn.commit()
    
    def match_exists(self, replay_id: str) -> bool:
        """
        Check if a match has already been analyzed.
        
        Args:
            replay_id: Ballchasing replay ID
            
        Returns:
            True if match exists in database
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM matches WHERE replay_id = ?", (replay_id,))
        return cursor.fetchone() is not None
    
    def save_match(self, replay_id: str, match_data: Dict, player_stats: Dict):
        """
        Save a match to the database.
        
        Args:
            replay_id: Ballchasing replay ID
            match_data: Full match details from API
            player_stats: Your specific player stats
        """
        stats = player_stats.get('stats', {})
        core = stats.get('core', {})
        boost = stats.get('boost', {})
        movement = stats.get('movement', {})
        positioning = stats.get('positioning', {})
        
        # Determine result (win/loss)
        team_color = self._find_player_team(match_data, player_stats)
        result = self._determine_result(match_data, team_color)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO matches (
                replay_id, date, duration, playlist, result, team_color,
                goals, assists, saves, shots, score, shooting_percentage,
                avg_boost, percent_zero_boost, percent_full_boost,
                amount_collected, amount_stolen,
                avg_speed, time_supersonic, percent_ground, percent_low_air, percent_high_air,
                percent_defensive_third, percent_offensive_third, percent_neutral_third,
                time_behind_ball, time_infront_ball,
                analyzed_at, stats_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            replay_id,
            match_data.get('date'),
            match_data.get('duration'),
            match_data.get('playlist_name'),
            result,
            team_color,
            # Core stats
            core.get('goals', 0),
            core.get('assists', 0),
            core.get('saves', 0),
            core.get('shots', 0),
            core.get('score', 0),
            core.get('shooting_percentage', 0),
            # Boost metrics
            boost.get('avg_amount', 0),
            boost.get('percent_zero_boost', 0),
            boost.get('percent_full_boost', 0),
            boost.get('amount_collected', 0),
            boost.get('amount_stolen', 0),
            # Movement metrics
            movement.get('avg_speed', 0),
            movement.get('time_supersonic_speed', 0),
            movement.get('percent_ground', 0),
            movement.get('percent_low_air', 0),
            movement.get('percent_high_air', 0),
            # Positioning metrics
            positioning.get('percent_defensive_third', 0),
            positioning.get('percent_offensive_third', 0),
            positioning.get('percent_neutral_third', 0),
            positioning.get('time_behind_ball', 0),
            positioning.get('time_infront_ball', 0),
            # Metadata
            datetime.now().isoformat(),
            json.dumps(stats)  # Store full stats for deep analysis
        ))
        self.conn.commit()
    
    def get_recent_matches(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent matches.
        
        Args:
            limit: Number of matches to retrieve
            
        Returns:
            List of match dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM matches 
            ORDER BY date DESC 
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_averages(self, last_n_matches: int = 10) -> Dict:
        """
        Calculate average stats over recent matches.
        
        Args:
            last_n_matches: Number of recent matches to include
            
        Returns:
            Dictionary of average stats
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                -- Core stats
                AVG(goals) as avg_goals,
                AVG(assists) as avg_assists,
                AVG(saves) as avg_saves,
                AVG(shots) as avg_shots,
                AVG(score) as avg_score,
                AVG(shooting_percentage) as avg_shooting_pct,
                
                -- Boost metrics
                AVG(avg_boost) as avg_boost,
                AVG(percent_zero_boost) as avg_percent_zero_boost,
                AVG(percent_full_boost) as avg_percent_full_boost,
                AVG(amount_collected) as avg_boost_collected,
                AVG(amount_stolen) as avg_boost_stolen,
                
                -- Movement metrics
                AVG(avg_speed) as avg_speed,
                AVG(time_supersonic) as avg_time_supersonic,
                AVG(percent_ground) as avg_percent_ground,
                AVG(percent_low_air) as avg_percent_low_air,
                AVG(percent_high_air) as avg_percent_high_air,
                
                -- Positioning metrics
                AVG(percent_defensive_third) as avg_percent_defensive_third,
                AVG(percent_offensive_third) as avg_percent_offensive_third,
                AVG(percent_neutral_third) as avg_percent_neutral_third,
                AVG(time_behind_ball) as avg_time_behind_ball,
                AVG(time_infront_ball) as avg_time_infront_ball,
                
                COUNT(*) as match_count
            FROM (
                SELECT * FROM matches 
                ORDER BY date DESC 
                LIMIT ?
            )
        """, (last_n_matches,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {}
    
    def get_match_by_id(self, replay_id: str) -> Optional[Dict]:
        """
        Get a specific match by replay ID.
        
        Args:
            replay_id: Ballchasing replay ID
            
        Returns:
            Match dictionary or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM matches WHERE replay_id = ?", (replay_id,))
        row = cursor.fetchone()
        if row:
            match = dict(row)
            # Parse the JSON stats back into a dictionary
            if match.get('stats_json'):
                match['full_stats'] = json.loads(match['stats_json'])
            return match
        return None
    
    def _find_player_team(self, match_data: Dict, player_stats: Dict) -> str:
        """Determine which team the player was on."""
        # Check if player is in blue team
        blue_players = match_data.get('blue', {}).get('players', [])
        for p in blue_players:
            if p.get('id') == player_stats.get('id'):
                return 'blue'
        return 'orange'
    
    def _determine_result(self, match_data: Dict, team_color: str) -> str:
        """Determine if the match was a win or loss."""
        blue_goals = match_data.get('blue', {}).get('stats', {}).get('core', {}).get('goals', 0)
        orange_goals = match_data.get('orange', {}).get('stats', {}).get('core', {}).get('goals', 0)
        
        if team_color == 'blue':
            return 'win' if blue_goals > orange_goals else 'loss'
        else:
            return 'win' if orange_goals > blue_goals else 'loss'
    
    def get_win_loss_averages(self, last_n_matches: int = 10) -> Dict:
        """
        Calculate separate averages for wins and losses.
        
        Args:
            last_n_matches: Number of recent matches to analyze
            
        Returns:
            Dictionary with 'wins' and 'losses' subdictionaries
        """
        cursor = self.conn.cursor()
        
        # Get averages for wins
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                AVG(goals) as avg_goals,
                AVG(assists) as avg_assists,
                AVG(saves) as avg_saves,
                AVG(shots) as avg_shots,
                AVG(shooting_percentage) as avg_shooting_pct,
                AVG(avg_boost) as avg_boost,
                AVG(percent_zero_boost) as avg_percent_zero_boost,
                AVG(percent_full_boost) as avg_percent_full_boost,
                AVG(amount_collected) as avg_boost_collected,
                AVG(avg_speed) as avg_speed,
                AVG(time_supersonic) as avg_time_supersonic,
                AVG(percent_ground) as avg_percent_ground,
                AVG(percent_low_air) as avg_percent_low_air,
                AVG(percent_high_air) as avg_percent_high_air,
                AVG(percent_defensive_third) as avg_percent_defensive_third,
                AVG(percent_offensive_third) as avg_percent_offensive_third,
                AVG(percent_neutral_third) as avg_percent_neutral_third,
                AVG(time_behind_ball) as avg_time_behind_ball
            FROM (
                SELECT * FROM matches 
                WHERE result = 'win'
                ORDER BY date DESC 
                LIMIT ?
            )
        """, (last_n_matches,))
        
        win_row = cursor.fetchone()
        wins = dict(win_row) if win_row else {}
        
        # Get averages for losses
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                AVG(goals) as avg_goals,
                AVG(assists) as avg_assists,
                AVG(saves) as avg_saves,
                AVG(shots) as avg_shots,
                AVG(shooting_percentage) as avg_shooting_pct,
                AVG(avg_boost) as avg_boost,
                AVG(percent_zero_boost) as avg_percent_zero_boost,
                AVG(percent_full_boost) as avg_percent_full_boost,
                AVG(amount_collected) as avg_boost_collected,
                AVG(avg_speed) as avg_speed,
                AVG(time_supersonic) as avg_time_supersonic,
                AVG(percent_ground) as avg_percent_ground,
                AVG(percent_low_air) as avg_percent_low_air,
                AVG(percent_high_air) as avg_percent_high_air,
                AVG(percent_defensive_third) as avg_percent_defensive_third,
                AVG(percent_offensive_third) as avg_percent_offensive_third,
                AVG(percent_neutral_third) as avg_percent_neutral_third,
                AVG(time_behind_ball) as avg_time_behind_ball
            FROM (
                SELECT * FROM matches 
                WHERE result = 'loss'
                ORDER BY date DESC 
                LIMIT ?
            )
        """, (last_n_matches,))
        
        loss_row = cursor.fetchone()
        losses = dict(loss_row) if loss_row else {}
        
        return {
            'wins': wins,
            'losses': losses,
            'total_wins': wins.get('count', 0),
            'total_losses': losses.get('count', 0)
        }
    
    def close(self):
        """Close database connection."""
        self.conn.close()


# Helper function to create database instance
def create_database(db_path: str = "data/matches.db") -> MatchDatabase:
    """Create a database instance."""
    return MatchDatabase(db_path)