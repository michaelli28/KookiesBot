from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from typing import Optional
import oauth2
import schoolopy
from pytz import timezone
import json
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


with open('config.json', 'r') as config:
        configfile = json.load(config)
        config.close()
cooldown = int(configfile['cooldown'])
times = int(configfile['numberoftimes'])


class school(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.timeforclass.start()

    def cog_unload(self):
        self.timeforclass.cancel()


    @tasks.loop(seconds=55)
    async def timeforclass(self):
        # channel = self.bot.get_channel(668863931200307248)
        channel2 = self.bot.get_channel(751142599418445824)

        now = datetime.datetime.now() 
        current_time = now.strftime("%H:%M")
        day_of_the_week = now.strftime("%A")
        if day_of_the_week=='Monday' or day_of_the_week=='Tuesday' or day_of_the_week=='Wednesday' or day_of_the_week=='Thursday' or day_of_the_week=='Friday': 
            if current_time == '11:50':
                # await channel.send("@hurb#7444 @zero2two0#5822 Class starts in 5 minutes!")
                await channel2.send("Class starts in 5 minutes!")

            elif current_time == '13:30':
                # await channel.send("@hurb#7444 @zero2two0#5822 Class starts in 5 minutes!")
                await channel2.send("Class starts in 5 minutes!")

            elif current_time == '15:40':
                # await channel.send("@hurb#7444 @zero2two0#5822 Class starts in 5 minutes!")
                await channel2.send("Class starts in 5 minutes!")
            else:
                pass
    # @commands.command(brief='Gets NotThatBot#3360\'s Schoology events, only for him')
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # @commands.is_owner()
    # async def events(self, ctx):
    #   sc = schoolopy.Schoology(schoolopy.Auth('254b46a2ce719be6b891fbf217028a5105f4f9215', 'd489775f4a578c226a7fc4476c7df9a5'))

    #   response = sc.get_events(section_id=2908224243)
    #   for i in range(len(response)):
    #     await ctx.send(response[i]['title'])

    # @commands.command(brief='Gets NotThatBot#3360\'s Schoology courses, only for him')
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # @commands.is_owner()
    # async def courses(self, ctx):
    #   sc = schoolopy.Schoology(schoolopy.Auth(
    #       '254b46a2ce719be6b891fbf217028a5105f4f9215', 'd489775f4a578c226a7fc4476c7df9a5'))
    #   response = sc.get_courses()

    #   await ctx.send(response)






    # @commands.command(name='set')
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def set_author(self, ctx):
    #   global author
    #   author = ctx.message.author
    #   await ctx.send(f'Author is set to {author.mention}')
    
    # @commands.command(name='channel')
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def set_channel(self, ctx):
    #   global channel
    #   channel = ctx.message.channel
    #   await ctx.send(f'Channel is set to {channel}')

    # @commands.command(brief='Gets NotThatBot#3360\'s grades, definitely only for him')
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # @commands.is_owner()
    # async def grades(self, ctx):
    #   sc = schoolopy.Schoology(schoolopy.Auth(
    #       '254b46a2ce719be6b891fbf217028a5105f4f9215', 'd489775f4a578c226a7fc4476c7df9a5'))
    #   response = sc.get_user_grades(user_id=59969976)
    #   print(response)
    

    # @commands.command(brief='Get the leaderboard!')
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def leaderboard(self, ctx):
    #   cluster = MongoClient(
    #       'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/KookiesBot?retryWrites=true&w=majority')
    #   db = cluster['KookiesBot']
    #   global collection
    #   collection = db['Xp']
    #   author = ctx.author.id
    #   user = await self.bot.fetch_user(author)
    #   result = collection.find({})
    #   sort = sorted(result, key=itemgetter('Xp'), reverse=True)
    #   embed = discord.Embed(color=random.randint(0, 0xffffff))
    #   embed.set_author(name='Leaderboard')
    #   embed.set_author(name=ctx.author.name, icon_url=user.avatar.url)
    #   place = 1
    #   for item in sort:
    #     embed.add_field(name=str(place)+') ' + '**' +
    #                     str(item['name'])+'**', value=str(item['Xp'])+' XP', inline=False)
    #     place += 1
    #   await ctx.send(embed=embed)






def setup(bot):
    bot.add_cog(school(bot))
