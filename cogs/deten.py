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


class deten(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            if message.channel.name.lower() == "detention":
                cluster = MongoClient(
                        'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/Other?retryWrites=true&w=majority')
                db = cluster.Other
                collection = db['Detention']
                id = str(message.guild.id)
                id += str(message.author.id)
                result = collection.find_one({'_id':id})
                if result == None:
                    return
                phrase = result["phrase"]
                times = result["times"]
                progress = result["progress"]
                if result != None and (phrase.lower() in message.content.lower()):
                    if (int(result["progress"]) + 1) == int(result["times"]):
                        role = get(message.author.guild.roles, name='Detention')
                        if role == None: 
                            return
                        await message.author.remove_roles(role)
                        roles = result['roles']
                        for role in roles:
                            try:
                                if role == '@everyone':
                                    pass
                                else:
                                    role = get(message.guild.roles, name=role)
                                    await message.author.add_roles(role)
                            except:
                                await message.channel.send(f'Unable to add role `{role.name}`')

                        collection.delete_many({'_id':id})
                        return await message.channel.send(f"{message.author.mention} has finished serving their detention by typing **{phrase}** in the detention channel **{times}** time(s)")
                    else:
                        collection.update_one({'_id': id}, {"$inc": {"progress": 1}})
                elif result != None and (phrase.lower() not in message.content.lower()):
                    return await message.channel.send(f'{message.author.mention} is in detention with the phrase **{phrase}** and needs to repeat it **{times-progress}** more time(s) to leave')




async def setup(bot):
	await bot.add_cog(deten(bot))
