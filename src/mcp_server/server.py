"""MCP Server for Rocket League match analysis."""

import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from .tools import (
    get_latest_match,
    get_win_loss_comparison,
    query_matches,
    get_player_averages,
    get_match_details
)

# Create MCP server instance
app = Server("gameinsight-rl")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools for the LLM to use.
    Each tool needs a name, description, and input schema.
    """
    return [
        Tool(
            name="get_latest_match",
            description="Get details about the most recent Rocket League match played. Returns full stats including goals, assists, saves, boost usage, positioning, and movement data.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_win_loss_comparison",
            description="Compare average stats between wins and losses to identify patterns. May highlight what stats correlate with winning vs losing. Takes the last N wins and last N losses (not necessarily consecutive games).",
            inputSchema={
                "type": "object",
                "properties": {
                    "last_n_matches": {
                        "type": "integer",
                        "description": "Number of wins and losses to compare (default 20)",
                        "default": 20
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="query_matches",
            description="Search and filter matches by various criteria. Can filter by result (win/loss), minimum and maximum stats (goals, saves), date ranges, and sort by different metrics. Useful for finding specific types of games or patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "result": {
                        "type": "string",
                        "enum": ["win", "loss"],
                        "description": "Filter by match result"
                    },
                    "min_goals": {
                        "type": "integer",
                        "description": "Minimum goals scored"
                    },
                    "max_goals": {
                        "type": "integer",
                        "description": "Maximum goals scored"
                    },
                    "min_saves": {
                        "type": "integer",
                        "description": "Minimum saves made"
                    },
                    "max_saves": {
                        "type": "integer",
                        "description": "Maximum saves made"
                    },
                    "date_after": {
                        "type": "string",
                        "description": "Only matches after this date (ISO format: 2024-10-01)"
                    },
                    "date_before": {
                        "type": "string",
                        "description": "Only matches before this date (ISO format: 2024-10-20)"
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["date", "goals", "score", "shooting_percentage"],
                        "description": "Sort results by this metric (default: date)",
                        "default": "date"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of matches to return (default 10)",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_player_averages",
            description="Get average for some stats stats over the player's recent matches (regardless of win/loss). Useful for seeing recent overall performance trends.",
            inputSchema={
                "type": "object",
                "properties": {
                    "last_n_matches": {
                        "type": "integer",
                        "description": "Number of recent matches to average (default 10)",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_match_details",
            description="Get comprehensive details for a specific match by its replay ID. Returns all available stats including boost management, positioning, movement, and scoring. Use this after query_matches to drill into specific games.",
            inputSchema={
                "type": "object",
                "properties": {
                    "replay_id": {
                        "type": "string",
                        "description": "The Ballchasing replay ID"
                    }
                },
                "required": ["replay_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool invocations from the LLM.
    Routes to the appropriate tool function and returns results.
    """
    try:
        if name == "get_latest_match":
            result = get_latest_match()
            
        elif name == "get_win_loss_comparison":
            last_n = arguments.get("last_n_matches", 20)
            result = get_win_loss_comparison(last_n_matches=last_n)
            
        elif name == "query_matches":
            result = query_matches(
                result=arguments.get("result"),
                min_goals=arguments.get("min_goals"),
                max_goals=arguments.get("max_goals"),
                min_saves=arguments.get("min_saves"),
                max_saves=arguments.get("max_saves"),
                date_after=arguments.get("date_after"),
                date_before=arguments.get("date_before"),
                sort_by=arguments.get("sort_by", "date"),
                limit=arguments.get("limit", 20)
            )
            
        elif name == "get_player_averages":
            last_n = arguments.get("last_n_matches", 10)
            result = get_player_averages(last_n_matches=last_n)
            
        elif name == "get_match_details":
            replay_id = arguments.get("replay_id")
            if not replay_id:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "replay_id is required"})
                )]
            result = get_match_details(replay_id)
            
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]
        
        # Convert result to JSON string
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())