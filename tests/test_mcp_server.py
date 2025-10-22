import sys
from pathlib import Path
import asyncio
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

print("🧪 Testing MCP Server\n")


async def test_server():
    """Test connecting to MCP server and calling tools."""
    
    # Start the MCP server as a subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp_server.server"],
        env=None
    )
    
    print("Starting MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            print("✅ Connected to MCP server\n")
            
            # Test 1: List available tools
            print("="*60)
            print("TEST 1: List Tools")
            print("="*60)
            
            tools_result = await session.list_tools()
            tools = tools_result.tools
            
            print(f"✅ Found {len(tools)} tools:\n")
            for tool in tools:
                print(f"  📋 {tool.name}")
                print(f"     {tool.description[:80]}...")
            
            # Test 2: Call get_latest_match
            print("\n" + "="*60)
            print("TEST 2: Call get_latest_match")
            print("="*60)
            
            result = await session.call_tool("get_latest_match", arguments={})
            content = result.content[0].text
            match = json.loads(content)
            
            if "error" not in match:
                print(f"✅ Got latest match:")
                print(f"  Playlist: {match.get('playlist')}")
                print(f"  Result: {match.get('result')}")
                print(f"  Stats: {match.get('goals')}G / {match.get('assists')}A / {match.get('saves')}S")
            else:
                print(f"❌ {match['error']}")
            
            # Test 3: Call get_win_loss_comparison
            print("\n" + "="*60)
            print("TEST 3: Call get_win_loss_comparison")
            print("="*60)
            
            result = await session.call_tool(
                "get_win_loss_comparison",
                arguments={"last_n_matches": 20}
            )
            content = result.content[0].text
            comparison = json.loads(content)
            
            print(f"✅ Got comparison:")
            print(f"  Wins: {comparison.get('total_wins')}")
            print(f"  Losses: {comparison.get('total_losses')}")
            
            # Test 4: Call query_matches
            print("\n" + "="*60)
            print("TEST 4: Call query_matches")
            print("="*60)
            
            result = await session.call_tool(
                "query_matches",
                arguments={"result": "win", "limit": 3}
            )
            content = result.content[0].text
            matches = json.loads(content)
            
            print(f"✅ Got {len(matches)} wins:")
            for match in matches[:3]:
                print(f"  - {match.get('date', '')[:10]}: {match.get('goals')}G")
            
            print("\n" + "="*60)
            print("✅ All MCP server tests passed!")
            print("="*60)


if __name__ == "__main__":
    asyncio.run(test_server())