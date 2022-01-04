import urllib
import json
import datetime
import re
import praw
import discord
import requests
from time import time
import numpy as np
import aiohttp
import io
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
import markovify
from discord.ext import commands
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.utils import get
from discord import Embed
from typing import Optional
import random
from pytz import timezone
import asyncio
from discord.ext import tasks
from operator import itemgetter
from discord.ext.commands.errors import BadArgument
import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet
import ksoftapi

kclient = ksoftapi.Client('1931343e09f8c6434c51af90c3a602ac06c29211')


with open('config.json', 'r') as config:
        configfile = json.load(config)
        config.close()
cooldown = int(configfile['cooldown'])
times = int(configfile['numberoftimes'])


client_secret = '5E8IY8h100TBQjMuU2OMHfum5v4'

client_id = 'Vca7Chk3l3eAuQ'
user_agent = 'windows:dunnowhattoputhere:v1.5 (by /u/Zealousideal-Cap5217)'


class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.df = pd.read_csv('./IMDB Dataset.csv')
        self.client = bot.client
        self.kclient = kclient
        self.ball = None
    # @commands.command(name='reddit', aliases=['red'], brief='Gets posts from subreddit, you can specify the timespan using a comma, with hour, day, week, month, year, or all. Example: ;reddit coding,month to get coding posts within a month, the default is day if not specified')
    # @commands.cooldown(times, cooldown, commands.BucketType.user)
    # async def reddit(self, ctx, *, subreddit):
    #     async with ctx.typing():
    #         # reddit = praw.Reddit(
    #         #     client_id=client_id,
    #         #     client_secret=client_secret,
    #         #     user_agent=user_agent
    #         # )
    #         # try:
    #         #     submission = reddit.subreddit(subreddit).random()
    #         # except:
    #         #     return await ctx.send(f'Subreddit {subreddit} not found')
    #         # if submission == None:
    #         #     return await ctx.send(f'Subreddit {subreddit} not found')
    #         # embed = discord.Embed(color=random.randint(
    #         #     0, 0xffffff), description=f'[Click here if image isn\'t loading]({submission.url})')
    #         # embed.set_image(url=submission.url)
    #         # embed.set_author(name=ctx.author.display_name,
    #         #                 icon_url=ctx.author.avatar.url)

    #         # embed.timestamp = datetime.datetime.utcnow()
    #         # return await ctx.send(embed=embed)
    #         if subreddit.find(',') != -1:

    #             list = subreddit.split(',', 1)
    #             subreddit = list[0]
    #             timespan = list[1]
    #             if timespan not in ["hour", "day", "week", "month", "year", "all"]:
    #                 return await ctx.send('Timespan must be hour, day, week, month, year or all. Example: ;reddit r/coding,day or ;reddit python,all you could also do ;reddit python without specifying a timestamp')
    #         else:
    #             timespan = 'day'
    #         try:
    #             reddit = await self.kclient.images.random_reddit(subreddit, span = timespan)
    #             embed = discord.Embed(color=random.randint(
    #                 0, 0xffffff), title=f'`{reddit.title}` by `{reddit.author}` in the `{reddit.subreddit}` subreddit', description=f'[Click here if image isn\'t loading]({reddit.image_url})')
    #             embed.set_image(url=reddit.image_url)
    #             embed.set_author(name=ctx.author.display_name,
    #                             icon_url=ctx.author.avatar.url)

    #             embed.timestamp = datetime.datetime.utcnow()
    #             return await ctx.send(embed=embed)

    #         except ksoftapi.errors.APIError as e:
    #             return await ctx.send(e)

    # @commands.command(brief='Gets a meme')
    # @commands.cooldown(times, cooldown, commands.BucketType.user)
    # async def meme(self, ctx):
    #     # with urllib.request.urlopen("https://meme-api.herokuapp.com/gimme") as url:
    #     #     data = json.load(url)
    #     #     if data['nsfw']==True:
    #     #         embed = discord.Embed(title='NOPE', color=random.randint(
    #     #             0, 0xffffff), description='DEFINITELY NOT, this meme is marked as nsfw')
    #     #         print(data['url'])

    #     #         embed.set_author(name=ctx.author.display_name,
    #     #                         icon_url=ctx.author.avatar.url)

    #     #         embed.timestamp = datetime.datetime.utcnow()
    #     #         return await ctx.send(embed=embed)

    #     #     else:
    #     #         embed = discord.Embed(title = '`'+str(data['title']) + '` from the `' + str(data['subreddit']) + '` subreddit by `' + str(data['author']) + '`',color=random.randint(
    #     #             0, 0xffffff), description='[Click here if image isn\'t loading](' + str(data['url']) + ')')
                    
    #     #         embed.set_image(url=data['url'])

    #     #         embed.set_author(name=ctx.author.display_name,
    #     #                         icon_url=ctx.author.avatar.url)

    #     #         embed.timestamp = datetime.datetime.utcnow()
    #     #         return await ctx.send(embed=embed)

    #     try:
    #         async with ctx.typing():
    #             reddit = await self.kclient.images.random_meme()
    #     except ksoftapi.NoResults:
    #         return await ctx.send('Error getting meme :cry:')
    #     else:
    #         embed = discord.Embed(color=random.randint(
    #             0, 0xffffff), title=f'`{reddit.title}` by `{reddit.author}` in the `{reddit.subreddit}` subreddit', description=f'[Click here if image isn\'t loading]({reddit.image_url})')
    #         embed.set_image(url=reddit.image_url)
    #         embed.set_author(name=ctx.author.display_name,
    #                         icon_url=ctx.author.avatar.url)

    #         embed.timestamp = datetime.datetime.utcnow()
    #         return await ctx.send(embed=embed)
    @commands.command(brief='Dispenses a cookie for you or someone else!', aliases=["kookie", "dispense", "cookies", "givemeacookie","cookiedispenser","iwantcookie"])
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def cookie(self, ctx, member: discord.Member=None):
            if member == None:
                return await ctx.send("Enjoy! :cookie")
            elif member.id==ctx.author.id:
                return await ctx.send("You gave yourself a cookie! What a smart decision :cookie:")
            else:
                return await ctx.send(f"{member.mention}, you can thank {ctx.author.mention} for the cookie! :cookie:")

    @commands.command(brief='Dispenses more cookies for the greedy ones :D', aliases=["givememorecookies"])
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def morecookies(self, ctx, member: discord.Member=None):
            if member == None:
                return await ctx.send("Be as greedy as you want with cookies! :cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie:")
            elif member.id==ctx.author.id:
                return await ctx.send("You gave yourself many cookies! What a smart decision :cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie:")
            else:
                return await ctx.send(f"{member.mention}, you can thank {ctx.author.mention} for the cookie donation! :cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie::cookie:")
    @commands.command(brief='Gets a awww image from reddit')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def aww(self, ctx):
        try:
            async with ctx.typing():
                reddit = await self.kclient.images.random_aww()
        except ksoftapi.NoResults:
            return await ctx.send('Error getting aww image :cry:')
        else:
            embed = discord.Embed(color=random.randint(
                0, 0xffffff), title=f'`{reddit.title}` by `{reddit.author}` in the `{reddit.subreddit}` subreddit', description=f'[Click here if image isn\'t loading]({reddit.image_url})')
            embed.set_image(url=reddit.image_url)
            embed.set_author(name=ctx.author.display_name,
                             icon_url=ctx.author.avatar.url)

            embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=embed)

    @commands.command(name='8ball', brief='Answer your yes/no questions')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _8ball(self, ctx, *, question=None):
        if (question) == None:
            return await ctx.send("Ask a question sir or ma\'am")
        lie = question.lower().find('are you')
        q1 = question.lower().find('lie')
        q2 = question.lower().find('lying')
        q3 = question.lower().find('accurate')
        
        if lie != -1:
            if q1 != -1 or q2 != -1 or q3 != -1:
                embed = discord.Embed(
                title='8ball response',
                color=random.randint(0, 0xffffff)
        )
                embed.add_field(name='Question', value=question, inline=False)
                embed.add_field(name='Answer', value='I\'m very accurate for your information. Don\'t question me!', inline=False)
                embed.set_author(name=ctx.author.display_name,
                                icon_url=ctx.author.avatar.url)
                embed.timestamp = datetime.datetime.utcnow()
                return await ctx.send(embed=embed)

        responses = ['Maybe', 'Hmm, try again later', 'Yes sir/ma\'am', 'No sir/ma\'am', 'You can count on it!', 'Guaranteed', 'How did you know?', 'Of course', 'I believe so', 'Nope', 'Definitely NOT', 'Very much so', 'The answer is NO', 'No (u)', 'Does money grow on trees? (Nope)', 'Is Magic better than Kookies? (NOOOO)', 'Calculating chances... 0%!!!!!', 'Calculating chances... 0%!!!!!', 'Calculating chances... error%!!!!! (this isn\'t a code error btw)', 'You wish', 'Yuppie', 'Debating... I\'m very sorry but the answer is noooooo', 'This answer isn\'t available at the moment', 'Do you believe in 8ball (that\'s the answer)', 'Nah', 'Sorry but no', 'Sorry but yes', 'Great job it\'s yes!', 'Great job it\'s no!', 'Nopaty nope!', '3rd Party influence detected, try again later', 'Too many questions detected', 'Yeah!', 'You guessed it!', 'Definitely!', 'Nooooooo', 'Hahahahaha no', 'Hahahaha good joke but still no']

        embed = discord.Embed(
            title='8ball response',
            color=random.randint(0, 0xffffff)
        )
        embed.add_field(name='Question', value=question, inline=False)
        embed.add_field(name='Answer', value=random.choice(
            responses), inline=False)
        embed.set_author(name=ctx.author.display_name,
                        icon_url=ctx.author.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)

    @commands.command(name='9ball', brief='Answer your yes/no questions with a bigger brain. This won\'t work all the time')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _9ball(self, ctx, *, question=None):
        if (question) == None:
            return await ctx.send("Ask a question sir or ma\'am")
        if self.ball == True:
            return await ctx.send('Please wait 15 seconds, 9ball is being used')
        else:
            self.ball = True

        
        me = self.bot.get_user(587068610237693963)
        await me.send('9ball Question:\n' + question)
        def check(m):
            return m.author.id == 587068610237693963 and m.channel == me.dm_channel
        try:
            response = await self.bot.wait_for('message', check=check, timeout=15)
        except asyncio.TimeoutError:
            await me.send('Timed out, please send a response to the 8ball question')
            embed = discord.Embed(
                title='9ball response',
                color=random.randint(0, 0xffffff)
            )
            embed.add_field(name='Question', value=question, inline=False)
            embed.add_field(name='Answer', value='The answer is not available at the moment, please try again later', inline=False)
            embed.set_author(name=ctx.author.display_name,
                            icon_url=ctx.author.avatar.url)
            embed.timestamp = datetime.datetime.utcnow()
            self.ball = None
            return await ctx.send(embed=embed)
        embed = discord.Embed(
            title='9ball response',
            color=random.randint(0, 0xffffff)
        )
        embed.add_field(name='Question', value=question, inline=False)
        embed.add_field(name='Answer', value=response.content, inline=False)
        embed.set_author(name=ctx.author.display_name,
                        icon_url=ctx.author.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        self.ball = False
        return await ctx.send(embed=embed)

    @commands.command(brief='Give money')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def gimme(self, ctx):
        return await ctx.send(f'{ctx.author.mention} has received {random.randint(100, 1000000)} dollars')

    @commands.command(brief='Says hello')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def hello(self, ctx):
        return await ctx.send("Hello " + ctx.message.author.mention)


    @commands.command(name='mimic', aliases=['mm'], brief='Mimics how you talk')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def mimicsentence(self, ctx):
        await ctx.send('Please send a small paragraph of sentences')

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg = await self.bot.wait_for('message', check=check)

        model = markovify.Text(msg.content)
        # generate 5 random sentences
        n = 1
        embed = discord.Embed(
            title=f'Sentences that {ctx.author.display_name} might say based off of a small paragraph')
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        for i in range(5):
            sentence = model.make_sentence()
            embed.add_field(name=f'Sentence {n})',
                            value=sentence, inline=False)
            n += 1
        return await ctx.send(embed=embed)


    @commands.command(aliases=['mood'], brief='Returns the mood of the sentence')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def sentiment(self, ctx, *, sentence):
        await ctx.send('Please wait while the AI does its work...')
        async with ctx.typing():

            # df.sentiment.value_counts().plot(kind='bar')

            # cleaning up the text
            self.df["review"] = self.df["review"].replace(
                r'[^A-Za-z0-9 ]+', '')
            self.df['review'] = self.df['review'].apply(lambda x: re.sub(
                r"((?<=^)|(?<= )).((?=$)|(?= ))", '', x).strip())
            self.df["review"] = self.df["review"].apply(
                lambda x: x.replace("<br /><br />", ""))
            await ctx.send('Reading the dataset... (this may take a minute)')
            vectorizer = CountVectorizer(stop_words='english')

            # buiding training and testing datasets

            X = self.df["review"]
            Y = self.df["sentiment"]

            X_train, X_test, y_train, y_test = train_test_split(
                X, Y, test_size=0.001, random_state=88
            )

            # tokenize each document into a vector of numbers
            X_vect = vectorizer.fit_transform(X_train)

            # training the model
            await ctx.send('Training the model now...')
            nb = MultinomialNB()
            nb.fit(X_vect, y_train)

            # gauging accuracy
            # y_pred = nb.predict(vectorizer.transform(X_test))
            # print(accuracy_score(y_test, y_pred))

            # function to predict on arbitrary text

            def text_predict(review):
                text_vector = vectorizer.transform([review])
                prediction = nb.predict(text_vector)
                return(prediction[0])

            embed = discord.Embed(
                title=f'The mood for the sentence: `{sentence}` was `{text_predict(sentence)}`', description='Was your sentence positive or negative, reply p for positive, n for negative', color=random.randint(0, 0xffffff))
            embed.set_author(name=ctx.author.display_name,
                             icon_url=ctx.author.avatar.url)
            embed.timestamp = datetime.datetime.utcnow()

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await ctx.send(embed=embed)
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=20)
            except asyncio.TimeoutError:
                return await ctx.send('Please respond with p or n for positive or negative within 20 seconds')
            if msg.content.lower() == 'p':
                await ctx.send(f'Thank you for responding {msg.content}, your data will be used to help make the AI smarter')
                response = f'"{sentence}",positive\n'
                file = open('IMDB Dataset.csv', 'a', newline='\n')
                file.write(response)
                file.close()

            elif msg.content.lower() == 'n':
                await ctx.send(f'Thank you for responding {msg.content}, your data will be used to help make the AI smarter')
                response = f'"{sentence}",negative\n'
                file = open('IMDB Dataset.csv', 'a', newline='\n')
                file.write(response)
                file.close()

            else:
                return await ctx.send('Please reply with p or n after using ;mood to help make the AI smarter')

    
    @commands.command(aliases=['mo'], brief='Becomes someone else')
    @commands.cooldown(1, 600, commands.BucketType.default)
    @commands.is_owner()
    async def moctopus(self, ctx, member: discord.Member, *, repeat):
        # name = 'avatar.png'
        await ctx.message.delete()
        botuser = ctx.guild.me
        # for role in botuser.roles:
        #     try:
        #         await botuser.remove_roles(role)
        #     except discord.errors.NotFound:
        #         pass
        try:
            await botuser.add_roles(member.top_role)
        except:
            pass
        # await user.avatar.url.save(name)
        avatar = await member.avatar.url.read()
        try:
            await self.bot.user.edit(avatar = avatar)
        except:
            await ctx.send('Can\'t change the avatar that fast')
        try:
            await self.bot.user.edit(nick = member.display_name)
        except:
            try:
                await self.bot.user.edit(username = member.display_name)
                return await ctx.send(repeat)
            except:
                await ctx.send('Too many users have this username')
                return await ctx.send(repeat)

    # @commands.command(name='insult', aliases=['roast'], brief='Insults people')
    # @commands.is_owner()
    # async def insult(self, ctx):
    #     """Insult generator"""
    #     url = 'https://www.rappad.co/api/battles/random_insult'
    #     try:
    #         user = ctx.message.mentions[0]
    #     except IndexError:
    #         return await ctx.send("Mention the person you want to insult")
    #     async with ctx.typing():
    #         async with self.client.get(url) as r:
    #             if r.status != 200:
    #                 return await ctx.send('API error, try again later')
    #             data = await r.json()

    #     insult_text = '. '.join(
    #         map(lambda s: s.strip().capitalize(), data['insult'].split('.')))
    #     return await ctx.send(f"{user.mention} {insult_text}")

    # @commands.command(name='chat', aliases=['aichat'], brief = 'Starts ai chat mode, type bye to stop')
    # @commands.max_concurrency(3, commands.BucketType.guild)
    # @commands.cooldown(1, 30, commands.BucketType.user)
    # async def _aichat(self, ctx):
    #     """Start AI chat mode"""
    #     def check(m):
    #         return m.author == ctx.author and not m.content.startswith(';')

    #     await ctx.send("Hello there!")
    #     url = 'https://some-random-api.ml/chatbot'
    #     while True:
    #         try:
    #             params = {'message': 'message'}
    #             msg = await self.bot.wait_for('message', check=check, timeout=45)
    #         except asyncio.TimeoutError:
    #             return await ctx.send("See you later :wave:")
    #         else:
    #             if 'bye' in msg.content.lower():
    #                 return await ctx.send("See you later :wave:")
    #             else:
    #                 params['message'] = msg.content
    #                 try:
    #                     async with ctx.typing():
    #                         async with self.client.get(url, params=params) as r:
    #                             response = await r.json()
    #                             print(response)
    #                             response = response['response']
    #                 except KeyError:
    #                     await ctx.send(response['error'])
    #                     continue
    #                 except discord.errors.HTTPException:
    #                     await ctx.send(response['error'])
    #                 await ctx.send(response)
def setup(bot):
	bot.add_cog(fun(bot))
