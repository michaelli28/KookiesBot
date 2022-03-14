import discord
import random
from discord.utils import get
from discord.ext import commands
from typing import Optional
from time import time
import discord_slash
from discord_slash import SlashCommand, cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

guild_ids = [751137949420224642] # Put your server ID in this array.

class slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="ping", guild_ids=guild_ids, description = 'description here')
    async def _ping(self,ctx):
        # await ctx.defer()
        return await ctx.send(f"Pong! ({self.bot.latency*1000}ms)")

    @cog_ext.cog_slash(name="test",
                guild_ids=guild_ids,
                description="This is just a test command, nothing more.",
                options=[
                create_option(
                    name="optone",
                    description="This is the first option we have.",
                    option_type=3,
                    required=False
                )
                ])
    async def test(self,ctx, optone: str):
        # await ctx.defer()
        return await ctx.send(content=f"I got you, you said {optone}!")

    @cog_ext.cog_slash(name="testing",
            guild_ids=guild_ids,
            description="This is just a test command, nothing more.",
            options=[
            create_option(
                name="optone",
                description="This is the first option we have.",
                option_type=3,
                required=False,
                choices=[
                create_choice(
                    name="ChoiceOne",
                    value="DOGE!"
                ),
                create_choice(
                    name="ChoiceTwo",
                    value="NO DOGE"
                )
                ]
            )
            ])
    async def testing(self, ctx, optone: str):
        # await ctx.defer()
        return await ctx.send(content=f"Wow, you actually chose {optone}? :(")

async def setup(bot):
    await bot.add_cog(slash(bot))