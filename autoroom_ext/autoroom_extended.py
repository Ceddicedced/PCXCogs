"""AutoRoom Extender cog for Red-DiscordBot by Ceddicedced."""

import asyncio

import discord
from discord.ext import tasks
from redbot.core import commands
from redbot.core.bot import Red


class AutoRoomExtended(commands.Cog):
    """AutoRoom Extended cog for Red-DiscordBot by Ceddicedced."""

    __author__ = "Ceddicedced"
    __version__ = "0.1.0"

    def __init__(self, bot: Red) -> None:
        """Initialize the cog."""
        self.bot = bot
        self.original_autoroom = None
        self.config = None
        self.update_channels = set()

    async def cog_load(self) -> None:
        """Load original autoroom cog."""
        # Check if AutoRoom cog is loaded
        if "AutoRoom" not in self.bot.cogs:
            msg = "AutoRoom cog is not loaded."
            raise RuntimeError(msg)
        self.original_autoroom = self.bot.get_cog("AutoRoom")
        # Log that AutoRoom is loaded
        self.autoroom_update_task.start()

    def cog_unload(self) -> None:
        """Clean up when the cog is unloaded."""
        self.autoroom_update_task.cancel()

    @tasks.loop(minutes=1)
    async def autoroom_update_task(self) -> None:
        """Update AutoRoom channels."""
        log_channel = self.bot.get_channel(752540655233925220)
        await log_channel.send("AutoRoom Extended update task started.")

        for autoroom_id in self.update_channels:
            source_channel = self.bot.get_channel(autoroom_id)
            if source_channel is None:
                await log_channel.send(f"Channel {autoroom_id} not found.")
                continue
            source_config = await self.original_autoroom.get_autoroom_source_config(
                source_channel
            )
            await log_channel.send(f"source_config: {str(source_config)[:2000]}")

        autoroom_ids: dict = await self.original_autoroom.config.all_channels()
        await log_channel.send(f"all_channels: {autoroom_ids}")
        for autoroom_id in autoroom_ids:
            await log_channel.send(f"channel: {autoroom_id}")
            if autoroom_ids[autoroom_id]["source_channel"] in self.update_channels:
                await log_channel.send(f"Updating channel: {autoroom_id}")
                await self.update_autoroom(autoroom_ids[autoroom_id])

    ### Commands ###

    @commands.group()
    @commands.guild_only()
    async def autoroomextended(self, ctx: commands.Context) -> None:
        """AutoRoom Extended cog commands."""

    # Update AutorRoom Group
    @autoroomextended.group()
    @commands.guild_only()
    async def update(self, ctx: commands.Context) -> None:
        """Update AutoRoom cog."""

    # Add AutoRoom channel
    @update.command()
    @commands.guild_only()
    async def update_add(
        self, ctx: commands.Context, autoroom_source: discord.VoiceChannel
    ) -> None:
        """Add AutoRoom channel."""
        config = await self.original_autoroom.get_autoroom_source_config(
            autoroom_source
        )
        if config is None:
            await ctx.send("This channel is not an AutoRoom channel.")
            return

        self.update_channels.add(autoroom_source.id)
        await ctx.send(f"Added {autoroom_source} to update list.")

    # Dev command groups
    @autoroomextended.group()
    @commands.is_owner()
    async def dev(self, ctx: commands.Context) -> None:
        """AutoRoom Extended dev commands."""

    @dev.command()
    async def test(self, ctx: commands.Context) -> None:
        """Test command."""
        await ctx.send("Test command.")

    # Return all loaded cogs
    @dev.command()
    async def cogs(self, ctx: commands.Context) -> None:
        """Return all loaded cogs."""
        cogs = self.bot.cogs
        await ctx.send(cogs)
