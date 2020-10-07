from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from typing import Optional
import urllib
import json
import discord
from discord.ext import commands
import datetime
import pymongo
from pymongo import MongoClient
import random
import re
import time
import praw
import requests

client_secret = '5E8IY8h100TBQjMuU2OMHfum5v4'

client_id = 'Vca7Chk3l3eAuQ'
user_agent = 'windows:dunnowhattoputhere:v1.5 (by /u/Zealousideal-Cap5217)'


class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reddit', aliases=['red'], brief='Gets posts from reddit')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reddit(self, ctx, *, subreddit):
        async with ctx.typing():
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            try:
                submission = reddit.subreddit(subreddit).random()
            except:
                return await ctx.send(f'Subreddit {subreddit} not found')
            embed = discord.Embed(color = random.randint(0, 0xffffff), description = f'[Click here if image isn\'t loading]({submission.url})')
            embed.set_image(url = submission.url)
            embed.set_author(name=ctx.author.name,
                            icon_url=ctx.author.avatar_url)

            embed.timestamp = datetime.datetime.now()
            return await ctx.send(embed=embed)
    @commands.command(brief='Gets a meme')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx):
        with urllib.request.urlopen("https://meme-api.herokuapp.com/gimme") as url:
            data = json.load(url)
            if data['nsfw']==True:
                embed = discord.Embed(title='NOPE', color=random.randint(
                    0, 0xffffff), description='DEFINITELY NOT, this meme is marked as nsfw')
                print(data['url'])

                embed.set_author(name=ctx.author.name,
                                icon_url=ctx.author.avatar_url)

                embed.timestamp = datetime.datetime.now()
                return await ctx.send(embed=embed)

            else:
                embed = discord.Embed(title = '`'+str(data['title']) + '` from the `' + str(data['subreddit']) + '` subreddit by `' + str(data['author']) + '`',color=random.randint(
                    0, 0xffffff), description='[Click here if image isn\'t loading](' + str(data['url']) + ')')
                    
                embed.set_image(url=data['url'])

                embed.set_author(name=ctx.author.name,
                                icon_url=ctx.author.avatar_url)

                embed.timestamp = datetime.datetime.now()
                return await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(fun(bot))
