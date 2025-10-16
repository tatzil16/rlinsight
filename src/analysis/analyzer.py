"""LLM-powered match analysis."""

import os
from typing import Dict, Optional
from openai import OpenAI
from .prompts import COACHING_SYSTEM_PROMPT, format_match_prompt


class MatchAnalyzer:
    """Analyzes Rocket League matches using LLM."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the analyzer.
        
        Args:
            api_key: OpenAI API key (or uses OPENAI_API_KEY from env)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-5-mini"
    
    def analyze_match(self, 
                    current_stats: Dict, 
                    win_loss_data: Dict,  # Changed from 'averages'
                    match_info: Dict) -> str:
        """
        Generate coaching feedback for a match.
        
        Args:
            current_stats: Stats from current match
            win_loss_data: Win/loss comparison data
            match_info: Match metadata (playlist, result, duration)
            
        Returns:
            Coaching feedback text
        """
        # Format the prompt
        user_prompt = format_match_prompt(current_stats, win_loss_data, match_info)
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": COACHING_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Check for refusal first (GPT-5 specific)
            if hasattr(response.choices[0].message, 'refusal') and response.choices[0].message.refusal:
                return f"⚠️ Model refused: {response.choices[0].message.refusal}"
            
            feedback = response.choices[0].message.content
            
            if not feedback or feedback.strip() == "":
                return "⚠️ Model returned empty response. Please try again."
            
            return feedback
            
        except Exception as e:
            return f"❌ Error generating feedback: {str(e)}"
    
    def format_discord_message(self, 
                               feedback: str, 
                               match_info: Dict,
                               current_stats: Dict) -> str:
        """
        Format feedback into a Discord-friendly message.
        
        Args:
            feedback: LLM-generated feedback
            match_info: Match metadata
            current_stats: Match stats
            
        Returns:
            Formatted Discord message
        """
        result_emoji = "🏆" if match_info.get('result') == 'win' else "💪"
        
        message = f"""🎮 **GameInsight Match Report** {result_emoji}

**Match:** {match_info.get('playlist', 'Unknown')} | {match_info.get('result', 'Unknown').upper()}
**Stats:** {current_stats.get('goals', 0)}G / {current_stats.get('assists', 0)}A / {current_stats.get('saves', 0)}S | {current_stats.get('shots', 0)} shots ({current_stats.get('shooting_percentage', 0):.0f}%)

**Coach's Analysis:**
{feedback}

---
_Next match starts soon—let's get it!_ 🚀
"""
        return message


def create_analyzer() -> MatchAnalyzer:
    """Create an analyzer instance."""
    return MatchAnalyzer()