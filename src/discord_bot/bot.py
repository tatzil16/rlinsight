"""Discord bot for posting match analysis."""

import discord
import os
from typing import Optional


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
