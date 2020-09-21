from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from typing import Optional
import oauth2
import schoolopy

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
class Schoology(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.timeforclass.start()

  def cog_unload(self):
    self.timeforclass.cancel()


  @tasks.loop(seconds=55)
  async def timeforclass(self):
    channel = self.bot.get_channel(668863931200307248)
    channel2 = self.bot.get_channel(751142599418445824)

    now = datetime.datetime.now() 
    current_time = now.strftime("%H:%M")
    day_of_the_week = now.strftime("%A")
    if day_of_the_week==('Monday' or 'Tuesday' or 'Wednesday' or 'Thursday' or 'Friday'): 
      if current_time == '07:55':
        await channel.send("@hurb#7444 @zero2two0#5822 Class starts in 5 minutes!")
        await channel2.send("Class starts in 5 minutes!")

      elif current_time == '09:55':
        await channel.send("@hurb#7444 @zero2two0#5822 Class starts in 5 minutes!")
        await channel2.send("Class starts in 5 minutes!")

      elif current_time == '11:55':
        await channel.send("@hurb#7444 @zero2two0#5822 Class starts in 5 minutes!")
        await channel2.send("Class starts in 5 minutes!")
      else:
        pass
  @commands.command(brief='Gets NotThatBot#3360\'s Schoology events, only for him')
  @commands.cooldown(1, 5, commands.BucketType.user)
  @commands.is_owner()
  async def events(self, ctx):
    sc = schoolopy.Schoology(schoolopy.Auth('254b46a2ce719be6b891fbf217028a5105f4f9215', 'd489775f4a578c226a7fc4476c7df9a5'))

    response = sc.get_events(section_id=2908224243)
    for i in range(len(response)):
      await ctx.send(response[i]['title'])

  @commands.command(brief='Gets NotThatBot#3360\'s Schoology courses, only for him')
  @commands.cooldown(1, 5, commands.BucketType.user)
  @commands.is_owner()
  async def courses(self, ctx):
    sc = schoolopy.Schoology(schoolopy.Auth(
        '254b46a2ce719be6b891fbf217028a5105f4f9215', 'd489775f4a578c226a7fc4476c7df9a5'))
    response = sc.get_courses()

    await ctx.send(response)
  @commands.command(brief='Gets the time')
  @commands.cooldown(1, 5, commands.BucketType.user)
  async def time(self, ctx):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")

    await ctx.send(current_time)
    
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

  @commands.command(brief='Gets NotThatBot#3360\'s grades, definitely only for him')
  @commands.cooldown(1, 5, commands.BucketType.user)
  @commands.is_owner()
  async def grades(self, ctx):
    sc = schoolopy.Schoology(schoolopy.Auth(
        '254b46a2ce719be6b891fbf217028a5105f4f9215', 'd489775f4a578c226a7fc4476c7df9a5'))
    response = sc.get_user_grades(user_id=59969976)
    print(response)
  

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
  #   embed.set_author(name=ctx.author.name, icon_url=user.avatar_url)
  #   place = 1
  #   for item in sort:
  #     embed.add_field(name=str(place)+') ' + '**' +
  #                     str(item['name'])+'**', value=str(item['Xp'])+' XP', inline=False)
  #     place += 1
  #   await ctx.send(embed=embed)



  @commands.command(aliases=['xp'], brief='Get your xp and level')
  @commands.cooldown(1, 5, commands.BucketType.user)
  async def rank(self, ctx, author=None):
    async with ctx.typing():
      cluster = MongoClient('mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/KookiesBot?retryWrites=true&w=majority')
      db = cluster['KookiesBot']
      global collection
      collection = db['Xp']

      if author == None:
        author = ctx.author.id

      else:
        author = (re.findall('<@!(.*?)>', author))[0]

      user = await self.bot.fetch_user(author)
      res = collection.find({})
      result = collection.find_one({'_id': int(author)}) 
      embed = discord.Embed(color=random.randint(0, 0xffffff))
      embed.set_author(name='Rank')
      sort = sorted(res, key=itemgetter('Xp'), reverse=True)
      rank = 1
      for item in sort:
        collection.update_one({'_id': item['_id']}, {"$set":{"rank": rank}}) 
        rank+=1
      try:
        embed.add_field(name='Total Xp', value='**'+str(result['Xp'])+'**')
      except:
        embed.add_field(name='Total Xp', value='**'+str(0)+'**')
      embed.add_field(name='Rank', value='**'+str(result['rank'])+'**')

      embed.set_author(name=result['name'], icon_url=user.avatar_url)
      embed.add_field(name='Level', value = '**'+ str(int(((12*result['Xp'])//800) ** 0.55))+'**')
      def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
      # @params:
      #     iteration   - Required  : current iteration (Int)
      #     total       - Required  : total iterations (Int)
      #     prefix      - Optional  : prefix string (Str)
      #     suffix      - Optional  : suffix string (Str)
      #     decimals    - Optional  : positive number of decimals in percent complete (Int)
      #     length      - Optional  : character length of bar (Int)
      #     fill        - Optional  : bar fill character (Str)
      #     printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))

        filledLength = int(length * iteration // total)

        bar = fill * filledLength + '-' * (length - filledLength)

        return (f'\r{prefix} |{bar}| {percent}% {suffix}')

      embed.add_field(name='Xp', value = printProgressBar(result['Xp'], 100000, prefix = '**'+str(result['Xp'])+"**", suffix = '**100,000**', length = 20))
      
      await ctx.send(embed=embed)

  @commands.Cog.listener()
  async def on_message(self, ctx):
    cluster = MongoClient('mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/KookiesBot?retryWrites=true&w=majority')
    db = cluster['KookiesBot']

    global collection
    collection = db['Xp']
    author = ctx.author.id
    res = collection.find({})
    result = collection.find_one({'_id': int(author)})
    chance = random.randint(1, 5)
    if chance == 5:
      # try:
      xp = random.randint(15, 25)
      collection.update_one({'_id': ctx.author.id}, {"$inc":{"Xp": xp}})

      sort = sorted(res, key=itemgetter('Xp'), reverse=True)
      rank = 1

      for item in sort:
        collection.update_one({'_id': item['_id']}, {"$set": {"rank": rank}})
        rank += 1

      try:
        new_lvl = int(((12*result['Xp']+xp)//800) ** 0.55)
        old_lvl = int(((12*result['Xp'])//800) ** 0.55)

        if new_lvl > old_lvl:
          await ctx.channel.send(f"Congrats {ctx.author.mention}! You reached level {new_lvl:,}!")

      except:
        xp = random.randint(15, 25)
        collection.insert_one(
            {'_id': ctx.author.id, 'name': ctx.author.name, "Xp": xp})
        sort = sorted(res, key=itemgetter('Xp'), reverse=True)
        rank = 1

        for item in sort:
          if item['rank'] != rank:
            collection.update_one({'_id': item['_id']}, {"$set": {"rank": rank}})
            rank += 1
        
      


def setup(bot):
  bot.add_cog(Schoology(bot))
