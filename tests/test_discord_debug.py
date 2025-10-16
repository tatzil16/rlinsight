import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import discord
import os

load_dotenv()

print("🔍 Discord Bot Debug Test\n")

# Create a simple client with logging
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"\n✅ on_ready() FIRED!")
    print(f"Bot user: {client.user}")
    print(f"Bot ID: {client.user.id}")
    print(f"\nServers (Guilds):")
    
    for guild in client.guilds:
        print(f"\n  Server: {guild.name}")
        print(f"  Channels:")
        for channel in guild.text_channels:
            print(f"    - #{channel.name}")
    
    await client.close()
    print("\n✅ Debug complete!")

@client.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Error in {event}")
    import traceback
    traceback.print_exc()

print("Connecting to Discord...")
print("(This should take 2-5 seconds)\n")

try:
    client.run(os.getenv("DISCORD_BOT_TOKEN"))
except Exception as e:
    print(f"❌ Failed to connect: {e}")