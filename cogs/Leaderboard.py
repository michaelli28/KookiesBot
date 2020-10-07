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
        embed.timestamp = datetime.datetime.now()
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        
        fields = []
        for entry in entries:
            fields.append(('**' + str(entry['rank']) + ') ' + entry['name']+'**', str(entry['Xp']) + ' XP'))
        self.place+=1

        return await self.write_page(menu, fields)


class Leaderboard(Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name='leaderboard', aliases=['lb'], brief='Shows the leaderboard')
    @commands.cooldown(1, 5, commands.BucketType.user)
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
        menu = MenuPages(source=HelpMenu(ctx, sort), delete_message_after=True)
        return await menu.start(ctx)

def setup(bot):
	bot.add_cog(Leaderboard(bot))
