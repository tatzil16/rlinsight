"""System prompts for the LLM coaching analysis."""

COACHING_SYSTEM_PROMPT = """You are an expert Rocket League coach providing post-match analysis. Your goal is to give actionable, specific feedback that helps players improve.

When analyzing a match, you have access to:
1. Current match stats
2. The player's averages in WINS vs LOSSES

**Key Insight:** Compare stats between wins and losses to identify patterns. For example:
- If avg_boost is 55 in wins but 45 in losses → boost management correlates with success
- If percent_defensive_third is 50% in wins but 60% in losses → they play too defensively when losing

Focus on:
1. **What Worked** - Stats that match their winning patterns
2. **What Hurt** - Stats that match their losing patterns  
3. **Actionable Adjustment** - One specific thing to change next game. Make it something strategic and back up with statistics rather than use statistics as a goal (e.g. say "Play more aggressive *backed by stats*" instead of "stay in the offensive third >22% of the time").

Guidelines:
- Be encouraging but data-driven
- Identify the 2-3 biggest differences between their wins and losses
- Give TWO clear action items based on the data
- Keep it concise (4-6 sentences)
- Use Rocket League terminology
- Consider whether this match was a win or a loss (in match info) and let that influence your feedback.

### Output Format:
Respond in **markdown** with the following structure:

**Key Strengths:**
- …

**Areas for Improvement:**
- …

**Actionable Tips:**
- …

**Next Game Goal:**
- …

Tone: Friendly, supportive, but critical coach who wants to see steady improvement."""


def format_match_prompt(current_stats: dict, win_loss_data: dict, match_info: dict) -> str:
    """
    Format match data into a prompt for the LLM.
    
    Args:
        current_stats: Stats from the current match
        win_loss_data: Separate averages for wins and losses
        match_info: Match metadata (playlist, result, etc.)
        
    Returns:
        Formatted prompt string
    """
    wins = win_loss_data.get('wins', {})
    losses = win_loss_data.get('losses', {})
    total_wins = win_loss_data.get('total_wins', 0)
    total_losses = win_loss_data.get('total_losses', 0)
    
    prompt = f"""Analyze this Rocket League match:

**Context:** Each stat reflects a gameplay domain — Core (scoring impact), Boost (efficiency and recovery; boost ranges from 0 to 100, small pads give 12 boost and large pads fill you to 100), Positioning (rotations and field control), and Movement (speed and pressure). Use these in win and loss data to identify key strengths and the most impactful improvement areas based on correlations with success.

**MATCH INFO:**
- Playlist: {match_info.get('playlist', 'Unknown')}
- Result: {match_info.get('result', 'Unknown').upper()}
- Duration: {match_info.get('duration', 0)} seconds

**THIS MATCH:**
Core: {current_stats.get('goals', 0)}G / {current_stats.get('assists', 0)}A / {current_stats.get('saves', 0)}S | {current_stats.get('shots', 0)} shots ({current_stats.get('shooting_percentage', 0):.1f}%)
Boost: Avg={current_stats.get('avg_boost', 0):.1f}, Zero={current_stats.get('percent_zero_boost', 0):.1f}%
Positioning: Def={current_stats.get('percent_defensive_third', 0):.1f}%, Off={current_stats.get('percent_offensive_third', 0):.1f}%
Movement: Speed={current_stats.get('avg_speed', 0)}, Supersonic={current_stats.get('time_supersonic', 0):.1f}s
"""

    # Add win/loss comparison if we have data
    if total_wins > 0 or total_losses > 0:
        prompt += f"\n**YOUR PATTERNS (last {total_wins} wins vs {total_losses} losses):**\n"
        
        if total_wins > 0 and total_losses > 0:
            # Show key comparisons
            prompt += f"""
In WINS you average:
- Goals: {wins.get('avg_goals', 0):.2f} | Assists: {wins.get('avg_assists', 0):.2f} | Saves: {wins.get('avg_saves', 0):.2f}
- Shooting %: {wins.get('avg_shooting_pct', 0):.1f}%
- Avg Boost: {wins.get('avg_boost', 0):.1f} | Zero Boost Time: {wins.get('avg_percent_zero_boost', 0):.1f}%
- Defensive Third: {wins.get('avg_percent_defensive_third', 0):.1f}% | Offensive Third: {wins.get('avg_percent_offensive_third', 0):.1f}%
- Avg Speed: {wins.get('avg_speed', 0):.0f} | Time Supersonic: {wins.get('avg_time_supersonic', 0):.1f}s

In LOSSES you average:
- Goals: {losses.get('avg_goals', 0):.2f} | Assists: {losses.get('avg_assists', 0):.2f} | Saves: {losses.get('avg_saves', 0):.2f}
- Shooting %: {losses.get('avg_shooting_pct', 0):.1f}%
- Avg Boost: {losses.get('avg_boost', 0):.1f} | Zero Boost Time: {losses.get('avg_percent_zero_boost', 0):.1f}%
- Defensive Third: {losses.get('avg_percent_defensive_third', 0):.1f}% | Offensive Third: {losses.get('avg_percent_offensive_third', 0):.1f}%
- Avg Speed: {losses.get('avg_speed', 0):.0f} | Time Supersonic: {losses.get('avg_time_supersonic', 0):.1f}s
"""
        elif total_wins > 0:
            prompt += f"\nOnly win data available ({total_wins} wins). Focus on maintaining winning patterns.\n"
        else:
            prompt += f"\nOnly loss data available ({total_losses} losses). Focus on breaking losing patterns.\n"
    else:
        prompt += "\n**NOTE:** No historical data yet. Provide general feedback based on this match.\n"
    
    prompt += "\nIdentify patterns and provide actionable coaching feedback."
    
    return prompt