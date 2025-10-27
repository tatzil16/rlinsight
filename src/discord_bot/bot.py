"""Discord bot for posting match analysis."""

import discord
import os
from typing import Optional
from src.discord_bot.mcp_handler import query_mcp


class GameInsightBot:
    """Discord bot for posting Rocket League match reports."""
    
    def __init__(self, token: Optional[str] = None, mention_user: Optional[str] = None):
        """
        Initialize the bot.
        
        Args:
            token: Discord bot token (or uses DISCORD_BOT_TOKEN from env)
            mention_user: Discord username to mention (or uses DISCORD_MENTION_USER from env)
        """
        self.token = token or os.getenv("DISCORD_BOT_TOKEN")
        if not self.token:
            raise ValueError("DISCORD_BOT_TOKEN not found")
        
        self.mention_user = mention_user or os.getenv("DISCORD_MENTION_USER", "")
        
        # Set up intents (permissions)
        intents = discord.Intents.default()
        intents.message_content = True  # Needed to read messages
        intents.members = True  # Needed to find users by username
        
        self.client = discord.Client(intents=intents)
        self.channel_name = "coach-feedback"
        self.target_channel = None
        self.user_to_mention = None
        
        # Set up event handlers
        self._setup_events()
    
    def _setup_events(self):
        """Set up Discord event handlers."""
        
        @self.client.event
        async def on_ready():
            """Called when bot connects to Discord."""
            print(f"✅ Bot logged in as {self.client.user}")
            
            # Find the target channel
            for guild in self.client.guilds:
                for channel in guild.text_channels:
                    if channel.name == self.channel_name:
                        self.target_channel = channel
                        print(f"✅ Found #{self.channel_name} in {guild.name}")
                        
                        # Find the user to mention
                        if self.mention_user:
                            for member in guild.members:
                                if member.name == self.mention_user or member.display_name == self.mention_user:
                                    self.user_to_mention = member
                                    print(f"✅ Found user to mention: @{member.display_name}")
                                    break
                            
                            if not self.user_to_mention:
                                print(f"⚠️  Could not find user '{self.mention_user}' in {guild.name}")
                        
                        return
            
            print(f"⚠️  Could not find #{self.channel_name} channel")

        @self.client.event
        async def on_message(message):
            """Called when any message is sent in channels the bot can see."""
            print(f"📨 Message received from {message.author}: {message.content[:50]}")
            
            # Ignore messages from the bot itself
            if message.author == self.client.user:
                print("   ⏭️  Ignoring (message from self)")
                return
            
            # Check if bot was mentioned
            if self.client.user in message.mentions:
                print(f"   🎯 Bot was mentioned! Handling query...")
                await self._handle_query(message)
            else:
                print(f"   ⏭️  Bot not mentioned in this message")
    
    async def post_report(self, message: str):
        """
        Post a match report to Discord.
        
        Args:
            message: Formatted message to post
        """
        if not self.target_channel:
            print(f"❌ No target channel found. Make sure #{self.channel_name} exists.")
            return
        
        try:
            # Add mention at the beginning if user found
            if self.user_to_mention:
                message = f"{self.user_to_mention.mention}\n\n{message}"
            
            await self.target_channel.send(message)
            print(f"✅ Posted report to #{self.channel_name}")
        except Exception as e:
            print(f"❌ Error posting to Discord: {e}")

    async def _handle_query(self, message):
        """
        Handle an @mention query from a user.
        
        Args:
            message: Discord message object
        """
        try:
            # Extract the question (remove the bot mention)
            question = message.content
            for mention in message.mentions:
                question = question.replace(f'<@{mention.id}>', '').strip()
            
            if not question:
                await message.channel.send("Hey! You mentioned me but didn't ask anything. Try: @GameInsight Why did I lose my last game?")
                return
            
            # Send "thinking" message
            thinking_msg = await message.channel.send("🤔 Analyzing your matches...")
            
            # Query MCP
            answer = await query_mcp(question)
            
            # Delete thinking message
            await thinking_msg.delete()
            
            # Send answer (handle long responses)
            if len(answer) <= 2000:
                await message.channel.send(answer)
            else:
                # Split into chunks if too long
                chunks = [answer[i:i+1900] for i in range(0, len(answer), 1900)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            
        except Exception as e:
            await message.channel.send(f"❌ Sorry, something went wrong: {str(e)}")
            print(f"Error handling query: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Start the bot (blocking call)."""
        self.client.run(self.token)
    
    async def start(self):
        """Start the bot (async, non-blocking)."""
        await self.client.start(self.token)
    
    async def close(self):
        """Close the bot connection."""
        await self.client.close()


def create_bot() -> GameInsightBot:
    """Create a bot instance."""
    return GameInsightBot()
