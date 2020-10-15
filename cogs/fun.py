import urllib
import json
import datetime
import re
import praw
import discord
import requests
from time import time
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
import markovify
from discord.ext import commands
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from typing import Optional
import random

import asyncio
from discord.ext import tasks
from operator import itemgetter
from discord.ext.commands.errors import BadArgument
import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet

client_secret = '5E8IY8h100TBQjMuU2OMHfum5v4'

client_id = 'Vca7Chk3l3eAuQ'
user_agent = 'windows:dunnowhattoputhere:v1.5 (by /u/Zealousideal-Cap5217)'


class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.df = pd.read_csv('./IMDB Dataset.csv')
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
        lie = question.lower().find('are you')
        if lie != -1:
            embed = discord.Embed(
            title='8ball response',
            color=random.randint(0, 0xffffff)
        )
            embed.add_field(name='Question', value=question, inline=False)
            embed.add_field(name='Answer', value='I\'m very accurate for your information. Don\'t question me!', inline=False)
            embed.set_author(name=ctx.author.display_name,
                            icon_url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.now()
            return await ctx.send(embed=embed)
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
        return await ctx.send(f'{ctx.author.mention} has received {random.randint(100, 1000000)} dollars')

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

    @commands.command(name='mimic', aliases=['mm'], brief='Mimics how you talk')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def mimicsentence(self, ctx):
        await ctx.send('Please send a small paragraph of sentences')

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg = await self.bot.wait_for('message', check=check)

        model = markovify.Text(msg.content)
        #generate 5 random sentences
        n = 1
        embed = discord.Embed(
            title=f'Sentences that {ctx.author.display_name} might say based off of a small paragraph')
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar_url)
        embed.timestamp = datetime.datetime.now()
        for i in range(5):
            sentence = model.make_sentence()
            embed.add_field(name=f'Sentence {n})',
                            value=sentence, inline=False)
            n += 1
        return await ctx.send(embed=embed)

    @commands.command(aliases=['def'], brief='Gives the definitions of a word without using an API')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def define(self, ctx, word):
        synsets = wordnet.synsets(word)
        embed = discord.Embed(title=f'Definition of the word: `{word}`')
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar_url)
        embed.timestamp = datetime.datetime.now()
        n = 1
        if len(synsets) == 0:
            return await ctx.send('No definitions found (this is kind of like AI so it\'s not perfect)')
        else:
            pass
        for synset in synsets:
            definition = synset.definition()
            embed.add_field(name=f'Definition {n})',
                            value=definition, inline=False)
            n += 1
        return await ctx.send(embed=embed)

    @commands.command(name='repeat', brief='Repeats your input')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def do_repeat(self, ctx, *, inp: str):
        """A simple command which repeats your input!
        Parameters
        ------------
        inp: str
            The input you wish to repeat.
        """
        message = ctx.message
        await message.delete()
        return await ctx.send(inp)

    @do_repeat.error
    async def do_repeat_handler(self, ctx, error):
        """A local Error Handler for our command do_repeat.
        This will only listen for errors in do_repeat.
        The global on_command_error will still be invoked after.
        """

        # Check if our required argument inp is missing.
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'inp':
                return await ctx.send("You forgot to give me input to repeat!")

    @commands.command(aliases=['mood'], brief='Returns the mood of the sentence')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sentiment(self, ctx, *, sentence):
        await ctx.send('Please wait while the AI does its work...')
        async with ctx.typing():

            # df.sentiment.value_counts().plot(kind='bar')

            #cleaning up the text
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

            #tokenize each document into a vector of numbers
            X_vect = vectorizer.fit_transform(X_train)

            #training the model
            await ctx.send('Training the model now...')
            nb = MultinomialNB()
            nb.fit(X_vect, y_train)

            #gauging accuracy
            # y_pred = nb.predict(vectorizer.transform(X_test))
            # print(accuracy_score(y_test, y_pred))

            #function to predict on arbitrary text

            def text_predict(review):
                text_vector = vectorizer.transform([review])
                prediction = nb.predict(text_vector)
                return(prediction[0])

            embed = discord.Embed(
                title=f'The mood for the sentence: `{sentence}` was `{text_predict(sentence)}`', description='Was your sentence positive or negative, reply p for positive, n for negative', color=random.randint(0, 0xffffff))
            embed.set_author(name=ctx.author.display_name,
                             icon_url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.now()

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

    

def setup(bot):
	bot.add_cog(fun(bot))
