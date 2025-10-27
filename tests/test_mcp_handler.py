import sys
from pathlib import Path
import asyncio

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.discord_bot.mcp_handler import query_mcp

load_dotenv()

print("🧪 Testing MCP Handler\n")


async def test_handler():
    """Test the MCP query handler."""
    
    questions = [
        "What happened in my last game?",
        "How does my boost management in wins compare to losses?",
        "Why did I lose my last loss?"
    ]
    
    for question in questions:
        print("="*60)
        print(f"Q: {question}")
        print("="*60)
        
        answer = await query_mcp(question)
        
        print(f"\nA: {answer}\n")
        print()


if __name__ == "__main__":
    asyncio.run(test_handler())