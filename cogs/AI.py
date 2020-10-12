import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
import markovify
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from typing import Optional

import discord
from discord.ext import commands
import datetime
import pymongo
from pymongo import MongoClient
import random
import re
import time

import asyncio
from discord.ext import tasks
from operator import itemgetter
from discord.ext.commands.errors import BadArgument
import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet

class ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.df = pd.read_csv('./IMDB Dataset.csv')
    @commands.command(name='mimic', aliases=['mm'], brief='Mimics how you talk')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def mimicsentence(self, ctx):
        await ctx.send('Please send a small paragraph of sentences')

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg = await self.bot.wait_for('message', check=check)

        model = markovify.Text(msg.content)
        #generate 5 random sentences
        n=1
        embed = discord.Embed(
            title=f'Sentences that {ctx.author.display_name} might say based off of a small paragraph')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.timestamp = datetime.datetime.now()
        for i in range(5):
            sentence = model.make_sentence()
            embed.add_field(name=f'Sentence {n})',
                            value=sentence, inline=False)
            n+=1
        return await ctx.send(embed=embed)
    @commands.command(aliases=['def'], brief='Gives the definitions of a word without using an API')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def define(self, ctx, word):
        synsets = wordnet.synsets(word)
        embed = discord.Embed(title=f'Definition of the word: `{word}`')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
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

    @commands.command(aliases=['mood'], brief='Returns the mood of the sentence')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sentiment(self, ctx, *, sentence):
        await ctx.send('Please wait while the AI does its work...')
        async with ctx.typing():


            # df.sentiment.value_counts().plot(kind='bar')


            #cleaning up the text
            self.df["review"] = self.df["review"].replace(r'[^A-Za-z0-9 ]+', '')
            self.df['review'] = self.df['review'].apply(lambda x: re.sub(
                r"((?<=^)|(?<= )).((?=$)|(?= ))", '', x).strip())
            self.df["review"] = self.df["review"].apply(lambda x: x.replace("<br /><br />", ""))
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
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.now()
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await ctx.send(embed=embed)
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=20)
            except asyncio.TimeoutError:
                return await ctx.send('Please respond with p or n for positive or negative within 20 seconds')
            if msg.content.lower()=='p':
                await ctx.send(f'Thank you for responding {msg.content}, your data will be used to help make the AI smarter')
                response = f'"{sentence}",positive\n'
                file = open('IMDB Dataset.csv','a', newline='\n')
                file.write(response)
                file.close()

            elif msg.content.lower()=='n':
                await ctx.send(f'Thank you for responding {msg.content}, your data will be used to help make the AI smarter')
                response = f'"{sentence}",negative\n'
                file = open('IMDB Dataset.csv','a', newline='\n')
                file.write(response)
                file.close()

            else:
                return await ctx.send('Please reply with p or n after using ;mood to help make the AI smarter')
            
def setup(bot):
	bot.add_cog(ai(bot))



