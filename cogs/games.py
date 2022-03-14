import random
import asyncio

import discord
from discord.ext import commands
#from .games import tictactoe, wumpus, hangman, minesweeper, twenty
import game.tictactoe as tictactoe
import game.twenty as twenty
import game.wumpus as wumpus
import game.hangman as hangman
import game.minesweeper as minesweeper
import json


with open('config.json', 'r') as config:
        configfile = json.load(config)
        config.close()
cooldown = int(configfile['cooldown'])
times = int(configfile['numberoftimes'])


class games(commands.Cog):
    """Play various Games"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='2048', brief='Starts a game of 2048, react to play')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def twenty(self, ctx):
        """Play 2048 game"""
        await twenty.play(ctx, self.bot)

    @commands.command(name='hangman', brief='Starts a game of hangman')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def hangman(self, ctx):
        """Play Hangman"""
        await hangman.play(self.bot, ctx)

    @commands.command(name='minesweeper', brief='Starts a game of minesweeper, play against yourself without the bot watching')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def minesweeper(self, ctx, columns=None, rows=None, bombs=None):
        """Play Minesweeper"""
        await minesweeper.play(ctx, columns, rows, bombs)

    @commands.command(name='rps', brief='Rock Paper Scissors, react to play')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
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
            return await ctx.send("Time's Up! :stopwatch:")
        else:
            await ctx.send(f"**:man_in_tuxedo_tone1:\t{reaction.emoji}\n:robot:\t{bot_emoji}**")
            # if conds
            if str(reaction.emoji) == bot_emoji:
                await ctx.send("**It's a Tie :ribbon:**")
            elif check_win(str(reaction.emoji), bot_emoji):
                await ctx.send("**You win :sparkles:**")
            else:
                await ctx.send("**I win :robot:**")

    @commands.command(name='toss', aliases=['flip'], brief='Flips a join')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def toss(self, ctx):
        """Flips a Coin"""
        coin = ['+ heads', '- tails']
        return await ctx.send(f"```diff\n{random.choice(coin)}\n```")


    @commands.command(name='tictactoe', aliases=['ttt'], brief='TicTacToe match, to play, type the column number and then the row number, starting from the top left at 1,1 where the bottom left is 3,3')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def ttt(self, ctx):
        """Play Tic-Tac-Toe"""
        await tictactoe.play_game(self.bot, ctx, chance_for_error=0.2)  # Win Plausible

    @commands.command(name='wumpus', brief='Starts a game of wumpus, can you kill the wumpus? (Search online for instructions if needed)')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def _wumpus(self, ctx):
        """Play Wumpus game"""
        await wumpus.play(self.bot, ctx)

async def setup(bot):
	await bot.add_cog(games(bot))
