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
from time import time
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
            embed.set_author(name=ctx.author.display_name,
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

                embed.set_author(name=ctx.author.display_name,
                                icon_url=ctx.author.avatar_url)

                embed.timestamp = datetime.datetime.now()
                return await ctx.send(embed=embed)

            else:
                embed = discord.Embed(title = '`'+str(data['title']) + '` from the `' + str(data['subreddit']) + '` subreddit by `' + str(data['author']) + '`',color=random.randint(
                    0, 0xffffff), description='[Click here if image isn\'t loading](' + str(data['url']) + ')')
                    
                embed.set_image(url=data['url'])

                embed.set_author(name=ctx.author.display_name,
                                icon_url=ctx.author.avatar_url)

                embed.timestamp = datetime.datetime.now()
                return await ctx.send(embed=embed)

    @commands.command(brief='Get your ping')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx):
        start = time()
        message = await ctx.send(f"Pong! Latency: {self.bot.latency*1000:,.0f} ms.")
        end = time()

        return await message.edit(content=f"Pong! Latency: {self.bot.latency*1000:,.0f} ms. Response time: {(end-start)*1000:,.0f} ms")


    @commands.command(name='8ball', brief='Answer your yes/no questions')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _8ball(self, ctx, *, question=None):
        if (question) == None:
            return await ctx.send("Ask a question sir or ma\'am")
        responses = ['Maybe', 'Hmm, try again later', 'Yes sir/ma\'am', 'No sir/ma\'am', 'You can count on it!', 'Guaranteed', 'How did you know?', 'Of course',
                    'I believe so', 'Nope', 'Definitely NOT', 'Very much so', 'The answer is NO', 'No (u)', 'Does money grow on trees?', 'Is magic better than Kookies? (NOOOO)']
        embed = discord.Embed(
            title='8ball response',
            color=random.randint(0, 0xffffff)
        )
        embed.add_field(name='Question', value=question, inline=False)
        embed.add_field(name='Answer', value=random.choice(
            responses), inline=False)
        embed.set_author(name=ctx.author.display_name,
                        icon_url=ctx.author.avatar_url)
        embed.timestamp = datetime.datetime.now()
        return await ctx.send(embed=embed)


    @commands.command(brief='Give money')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gimme(self, ctx):
        return await ctx.send(f'{ctx.author.mention} has recieved {random.randint(100, 1000000)} dollars')

    @commands.command(brief='Gets the time')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def time(self, ctx):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        return await ctx.send(current_time)

    @commands.command(brief='Get your id')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def id(self, ctx):
        author = ctx.message.author.id
        return await ctx.send(author)


    @commands.command(brief='Says hello')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hello(self, ctx):
        return await ctx.send("Hello " + ctx.message.author.mention)


    @commands.command(brief='Gets news from CNN')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def news(self, ctx, *, search):
        num_query = search.split(',', 1)
        number_of_results = num_query[0]

        try:
            searchq = num_query[1]
        except:
            number_of_results = 1
            searchq = num_query

        query_string1 = urllib.parse.urlencode({'q': searchq})
        query_string1 = query_string1.encode('utf-8')

        req1 = urllib.request.Request(
            'https://news.google.com/', query_string1,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )

        resp1 = urllib.request.urlopen(req1)
        respData1 = resp1.read()

        search_results1 = re.findall(
            '"https://www\.cnn\.com/(.*?)"', str(respData1))
        results = {}
        for n in range(int(number_of_results)):
            results[n+1] = ('https://www.cnn.com/search?' + search_results1[n])
        return await ctx.send(results)


def setup(bot):
	bot.add_cog(fun(bot))
