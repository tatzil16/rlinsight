"""MCP query handler for Discord interactions."""

import sys
import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI


# System prompt optimized for Discord (concise responses)
DISCORD_SYSTEM_PROMPT = """You are an expert Rocket League coach providing analysis and answering questions through Discord.

When analyzing matches:
1. ALWAYS compare to win/loss patterns (use get_win_loss_comparison)
2. Look at multiple stat categories: scoring, boost, positioning, movement
3. For specific match questions, drill into details with get_match_details
4. Give concrete, actionable recommendations

IMPORTANT: 
- Keep responses concise (2-4 paragraphs max for Discord)
- Use multiple tool calls to build complete analysis. You can chain tool calls together to build a thorough analysis.
- Be direct and specific

You have these tools available:
- get_latest_match: Get most recent match
- get_win_loss_comparison: Compare win vs loss patterns
- query_matches: Search matches by criteria
- get_player_averages: Get overall averages
- get_match_details: Deep dive into specific match
"""


async def query_mcp(question: str, max_iterations: int = 10) -> str:
    """
    Query the MCP server with a natural language question.
    
    Args:
        question: User's question
        max_iterations: Max number of LLM iterations (default 10)
        
    Returns:
        LLM's answer
    """
    # 1. Initialize OpenAI client
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # 2. Start MCP server
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.mcp_server.server"],
        env=None
    )
    
    # 3. Start MCP session (using context manager)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()
            
            # 4. Get available tools
            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools
            
            # Convert to OpenAI format
            openai_tools = []
            for tool in mcp_tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
            
            # 5. Set up initial messages
            messages = [
                {"role": "system", "content": DISCORD_SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ]
            
            # 6. Conversation loop
            for iteration in range(max_iterations):
                # 6.1. Call LLM
                response = await openai_client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto"
                )
                
                message = response.choices[0].message
                
                # 6.2. Check for refusal (GPT-5 specific)
                if hasattr(message, 'refusal') and message.refusal:
                    return f"⚠️ Unable to process: {message.refusal}"
                
                # 6.3. Check for empty response
                if not message.content and not message.tool_calls:
                    return "⚠️ No response generated. Please try rephrasing your question."
                
                # Check if LLM wants to call tools
                if message.tool_calls:
                    # 6.3.1. Add assistant's message to history
                    messages.append({
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in message.tool_calls
                        ]
                    })
                    
                    # 6.3.2. Execute each tool call
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        # Call the MCP tool
                        result = await session.call_tool(tool_name, tool_args)
                        tool_result = result.content[0].text
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })
                
                else:
                    # 7. LLM has final answer - return it
                    return message.content
            
            # If we hit max iterations
            return "⚠️ Analysis took too long. Please try a simpler question."
