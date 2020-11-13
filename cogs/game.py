import random
import asyncio

import discord
from discord.ext import commands
#from .games import tictactoe, wumpus, hangman, minesweeper, twenty
import games.tictactoe as tictactoe
import games.twenty as twenty
import games.wumpus as wumpus
import games.hangman as hangman
import games.minesweeper as minesweeper
class Game(commands.Cog):
    """Play various Games"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='2048')
    async def twenty(self, ctx):
        """Play 2048 game"""
        await twenty.play(ctx, self.bot)

    @commands.command(name='hangman', aliases=['hang'])
    async def hangman(self, ctx):
        """Play Hangman"""
        await hangman.play(self.bot, ctx)

    @commands.command(name='minesweeper', aliases=['ms'])
    async def minesweeper(self, ctx, columns=None, rows=None, bombs=None):
        """Play Minesweeper"""
        await minesweeper.play(ctx, columns, rows, bombs)

    @commands.command(name='rps', aliases=['rockpaperscissors'])
    async def rps(self, ctx):
        """Play Rock, Paper, Scissors game"""
        def check_win(p, b):
            if p == '🌑':
                return False if b == '📄' else True
            if p == '📄':
                return False if b == '✂' else True
            # p=='✂'
            return False if b == '🌑' else True

        async with ctx.typing():
            reactions = ['🌑', '📄', '✂']
            game_message = await ctx.send("**Rock Paper Scissors**\nChoose your shape:", delete_after=15.0)
            for reaction in reactions:
                await game_message.add_reaction(reaction)
            bot_emoji = random.choice(reactions)

        def check(reaction, user):
            return user != self.bot.user and user == ctx.author and (str(reaction.emoji) == '🌑' or '📄' or '✂')
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Time's Up! :stopwatch:")
        else:
            await ctx.send(f"**:man_in_tuxedo_tone1:\t{reaction.emoji}\n:robot:\t{bot_emoji}**")
            # if conds
            if str(reaction.emoji) == bot_emoji:
                await ctx.send("**It's a Tie :ribbon:**")
            elif check_win(str(reaction.emoji), bot_emoji):
                await ctx.send("**You win :sparkles:**")
            else:
                await ctx.send("**I win :robot:**")

    @commands.command(name='toss', aliases=['flip'])
    async def toss(self, ctx):
        """Flips a Coin"""
        coin = ['+ heads', '- tails']
        return await ctx.send(f"```diff\n{random.choice(coin)}\n```")


    @commands.command(name='tictactoe', aliases=['ttt'])
    async def ttt(self, ctx):
        """Play Tic-Tac-Toe"""
        await tictactoe.play_game(self.bot, ctx, chance_for_error=0.2)  # Win Plausible

    @commands.command(name='wumpus')
    async def _wumpus(self, ctx):
        """Play Wumpus game"""
        await wumpus.play(self.bot, ctx)
