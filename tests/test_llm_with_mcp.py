import sys
from pathlib import Path
import asyncio
import json
import os

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

print("🤖 Testing LLM with MCP Tools\n")


async def ask_llm_with_tools(question: str):
    """
    Ask the LLM a question and let it use MCP tools to answer.
    """
    
    # Initialize OpenAI client
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Start MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp_server.server"],
        env=None
    )
    
    print(f"Question: {question}\n")
    print("Starting MCP server and connecting to GPT-4o-mini...\n")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize MCP session
            await session.initialize()
            
            # Get available tools
            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools
            
            print(f"✅ Connected! LLM has access to {len(mcp_tools)} tools\n")
            
            # Convert MCP tools to OpenAI format
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
            
            # Initial messages
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert Rocket League coach providing deep, data-driven analysis.

                    When analyzing matches:
                    1. ALWAYS compare to win/loss patterns (use last_n_matches=10-20 for good sample size)
                    2. Look at MULTIPLE stats categories: scoring, boost management, positioning, movement
                    3. When asked about a single match, use follow up toools to drill into the specific match details to find root causes
                    4. Give concrete, actionable recommendations when applicable
                    5. 

                    IMPORTANT: Don't hesitate to make multiple tool calls to build a complete picture. 
It's better to gather comprehensive data across several calls than to rush to conclusions.
Use as many tool calls as needed - you can chain together query_matches, get_match_details, 
and get_win_loss_comparison to build thorough analysis."""
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
            
            # Conversation loop (allow multiple tool calls)
            max_iterations = 10
            for iteration in range(max_iterations):
                print(f"--- Iteration {iteration + 1} ---")
                
                # Call LLM
                response = await openai_client.chat.completions.create(
                    model="gpt-5-mini",  # ← Changed from gpt-4o-mini
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto"
                )
                
                message = response.choices[0].message

                # Check for refusal (GPT-5 specific)
                if hasattr(message, 'refusal') and message.refusal:
                    print(f"⚠️ LLM refused: {message.refusal}")
                    break

                # Check for empty content
                if not message.content and not message.tool_calls:
                    print("⚠️ LLM returned empty response")
                    break

                # Check if LLM wants to call tools
                if message.tool_calls:
                    print(f"🔧 LLM is calling {len(message.tool_calls)} tool(s):")
                    
                    # Add assistant's message to history
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
                    
                    # Execute each tool call
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        print(f"   → {tool_name}({json.dumps(tool_args)})")
                        
                        # Call the MCP tool
                        result = await session.call_tool(tool_name, tool_args)
                        tool_result = result.content[0].text
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })
                        
                        print(f"   ✅ Got result ({len(tool_result)} chars)")
                    
                    print()
                
                else:
                    # LLM has final answer
                    print("💬 LLM's Answer:")
                    print("="*60)
                    print(message.content)
                    print("="*60)
                    break
            
            else:
                print("⚠️ Max iterations reached")


async def main():
    """Run test questions."""
    
    # Test Question 1: Simple query
    print("="*60)
    print("TEST 1: Simple Query")
    print("="*60 + "\n")
    
    #await ask_llm_with_tools("What happened in my last game?")
    
    print("\n\n")
    
    # Test Question 2: Comparison query
    print("="*60)
    print("TEST 2: Comparison Query")
    print("="*60 + "\n")
    
    #await ask_llm_with_tools("How does my boost management in wins compare to losses?")
    
    print("\n\n")
    
    # Test Question 3: Complex query requiring multiple tools
    print("="*60)
    print("TEST 3: Complex Query")
    print("="*60 + "\n")
    
    await ask_llm_with_tools("Why did I lose my last loss? Compare it to how I play when I win.")
    
    print("\n✅ All tests complete!")


if __name__ == "__main__":
    asyncio.run(main())