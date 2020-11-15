from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from typing import Optional
from pytz import timezone
import discord
from discord.ext import commands
import datetime
import pymongo
from pymongo import MongoClient
import random
import re
import time
import json
import asyncio
from discord.ext import tasks
from operator import itemgetter


with open('config.json', 'r') as config:
        configfile = json.load(config)
        config.close()
cooldown = int(configfile['cooldown'])
times = int(configfile['numberoftimes'])


class menu(MenuPages):
    def reaction_check(self, payload):

        if payload.message_id != self.message.id:
            return False
        if payload.user_id in {743859420798124043}:
            return False

        return payload.emoji in self.buttons


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 30, fill = '█'):
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

class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        self.place = 1
        super().__init__(data, per_page=10)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(
                title=f"Leaderboard for {self.ctx.guild.name}", color=random.randint(0, 0xffffff))
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(
                text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} users")
        embed.timestamp = datetime.datetime.utcnow()
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        
        fields = []
        for entry in entries:
            try:
                fields.append(('**' + str(entry['rank']) + ') ' + entry['name']+'**', str(entry['Xp']) + ' XP'))
            except KeyError:
                return await self.ctx.send('This server has no leaderboard yet... send messages to get on the leaderboard')

        self.place+=1

        return await self.write_page(menu, fields)


class levels(Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name='leaderboard', aliases=['lb'], brief='Shows the leaderboard')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def show_leaderboard(self, ctx):
        async with ctx.typing():
            cluster = MongoClient('mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/KookiesBot?retryWrites=true&w=majority')

        db = cluster.KookiesBot

        global collection
        try:
            collection = db[ctx.guild.name]
        except:
            db.createCollection(ctx.guild.name)
            collection = db[ctx.guild.name]
            return await ctx.send('No one is on the leaderboard yet... send more messages to get on the leaderboard')
        result = collection.find({})

        sort = sorted(result, key=itemgetter('Xp'), reverse=True)
        rank=1
        for item in sort:
            collection.update_one({'_id': item['_id']}, {"$set":{"rank": rank}}) 
            rank+=1
        menu1 = menu(source=HelpMenu(ctx, sort), delete_message_after=True)
        return await menu1.start(ctx)

    @commands.command(aliases=['xp'], brief='Get your xp and level')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def rank(self, ctx, author: discord.Member = None):
        async with ctx.typing():

            cluster = MongoClient(
                'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/KookiesBot?retryWrites=true&w=majority')

            db = cluster.KookiesBot
            global collection
            try:
                collection = db[ctx.guild.name]
            except:
                db.createCollection(ctx.guild.name)
                collection = db[ctx.guild.name]
            if author == None:
                author = ctx.author.id

            else:
                author = author.id

            user = await self.bot.fetch_user(author)
            res = collection.find({})
            result = collection.find_one({'_id': int(author)})
            try:
                if result['Xp'] == 0:
                    return await ctx.send(f'{user.mention} has no xp, send more messages to gain xp')
            except:
                return await ctx.send(f'{user.mention} has no xp, send more messages to gain xp')

            embed = discord.Embed(color=random.randint(0, 0xffffff))
            embed.set_author(name='Rank')
            sort = sorted(res, key=itemgetter('Xp'), reverse=True)
            rank = 1
            for item in sort:
                collection.update_one({'_id': item['_id']}, {
                                      "$set": {"rank": rank}})
                rank += 1
            try:
                embed.add_field(
                    name=f'Total Xp in {ctx.guild.name}', value='**'+str(result['Xp'])+'**')
            except:
                embed.add_field(
                    name=f'Total Xp in {ctx.guild.name}', value='**'+str(0)+'**')

            embed.add_field(name='Rank', value='**'+str(result['rank'])+'**')

            embed.set_author(name=result['name'], icon_url=user.avatar_url)
            embed.add_field(name='Level', value='**' +
                            str(int(((12*result['Xp'])//800) ** 0.55))+'**')

            embed.add_field(name='Xp', value=printProgressBar(
                result['Xp'], 100000, prefix='**'+str(result['Xp'])+"**", suffix='**100,000**'))
            embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        else:
            with open("cooldown.json", "r") as f:
                cooldowns = json.load(f)
                f.close()
            try:
                previous = datetime.datetime.strptime(
                    cooldowns[str(ctx.author.id)], '%Y-%m-%d %H:%M:%S.%f')
            except:
                previous = datetime.datetime.strptime(
                    cooldowns['start'], '%Y-%m-%d %H:%M:%S.%f')

            time_difference = (datetime.datetime.utcnow() -
                               previous).total_seconds()
            if time_difference < 60:
                return

            else:
                cluster = MongoClient(
                    'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/KookiesBot?retryWrites=true&w=majority')
                db = cluster.KookiesBot

                global collection
                try:
                    collection = db[ctx.guild.name]
                except:
                    db.createCollection(ctx.guild.name)
                    collection = db[ctx.guild.name]

                author = ctx.author.id
                res = collection.find({})

                xp = random.randint(15, 22)
                try:
                    
                    collection.update_one({'_id': ctx.author.id}, {
                                          "$inc": {"Xp": xp}})
                except:
                    pass

                sort = sorted(res, key=itemgetter('Xp'), reverse=True)
                rank = 1

                for item in sort:
                    collection.update_one({'_id': item['_id']}, {
                                          "$set": {"rank": rank}})
                    rank += 1

                try:
                    result = collection.find_one({'_id': author})
                    new_lvl = int(((12*result['Xp'])//800) ** 0.55)
                    old_lvl = int(((12*result['Xp']-xp)//800) ** 0.55)
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
                            collection.update_one({'_id': item['_id']}, {
                                                  "$set": {"rank": rank}})
                            rank += 1
                with open("cooldown.json", "r") as f:
                    cooldowns = json.load(f)
                    # del cooldowns[str(ctx.author.id)]
                    cooldowns[str(ctx.author.id)] = str(
                        datetime.datetime.utcnow())
                    f.close()

                with open("cooldown.json", "w") as f:
                    json.dump(cooldowns, f)
                    f.close()
                return

def setup(bot):
	bot.add_cog(levels(bot))
