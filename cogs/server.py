from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.utils import get
from discord import Embed
from typing import Optional, Union
import json
import discord
from discord.ext import commands
import datetime
import pymongo
from pymongo import MongoClient
import random
import re
import time
from collections import Counter
import asyncio
from discord.ext import tasks
from pytz import timezone
from discord.ext.commands.errors import BadArgument



with open('config.json', 'r') as config:
        configfile = json.load(config)
        config.close()
cooldown = int(configfile['cooldown'])
times = int(configfile['numberoftimes'])


class server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        

        log = self.bot.get_guild(765941083254947911)
        asians = self.bot.get_guild(751137949420224642)
        bikeguild = self.bot.get_guild(764977928307998750)

        if message.guild == log or message.guild == asians:
            return

        channel = log.get_channel(768939732280803358)
        channelbike = log.get_channel(768945060753702913)
        if message.guild == bikeguild:
            channel = channelbike

        if message.author.id != self.bot.user.id:
            try:
                embed = discord.Embed(color=random.randint(
                    0, 0xffffff), description=f'Message sent by {message.author.mention} in {message.channel.mention} in {message.guild.name} [Jump to Message]({message.jump_url})')
                embed.add_field(name=f'{message.content}', value=f'\u200B')
                embed.set_author(name=message.author.display_name,
                                icon_url=message.author.avatar_url)

                embed.timestamp = datetime.datetime.utcnow()
                await channel.send(embed=embed)
            except:
                if message.attachments:
                    embed = discord.Embed(color=random.randint(
                        0, 0xffffff), description=f'Message sent by {message.author.mention} in {message.channel.mention} in {message.guild.name} [Jump to Message]({message.jump_url})')
                    for attachment in message.attachments:
                        new = await attachment.to_file()
                        await channel.send(file=new)
                        embed.set_image(url=f'{attachment.url}')

                    embed.set_author(name=message.author.display_name,
                                    icon_url=message.author.avatar_url)
                    embed.timestamp = datetime.datetime.utcnow()
                    await channel.send(embed=embed)

            if message.embeds:
                for embed in message.embeds:
                    await channel.send(embed=embed)
        return

    @commands.command(brief='Creates a channel')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def createchannel(self, ctx, *, name):
        guild = ctx.message.guild
        await guild.create_text_channel(name)
        return await ctx.send(f'Created text channel {name}')

    @commands.command(brief='Creates a voice channel')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def createvoicechannel(self, ctx, *, name):
        guild = ctx.message.guild
        await guild.create_voice_channel(name)
        return await ctx.send(f'Created voice channel {name}')

    # @commands.command(brief = 'Calculates the number of days until the end of school')
    # @commands.cooldown(times, cooldown, commands.BucketType.user)
    # async def countdown(self, ctx):
    #     if ctx.guild.id != 751137949420224642:
    #         return await ctx.send('This command is not available in this guild')
    #     else:
    #         today = datetime.date.today()
    #         end = datetime.date(2021, 6, 16)
    #         diff = end - today
    #         return await ctx.send(f'There are **{diff.days}** days left until school is over! (Including weekends)')
    @commands.command(brief='Edits a text channel')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def editchannel(self, ctx, name: discord.TextChannel, *, nname: Optional[str] = None, slowmode: Optional[int] = None):
        rindex = 0
        for char in name:
            try:
                name.find('_')
                rindex += 1
            except:
                pass

        name = name.replace('_', " ", rindex)
        if nname != None:
            await name.edit(name=nname)
            await ctx.send(f'Changed the name of channel {name.name} to {nname}')
        if slowmode != None:
            await name.edit(slowmode_delay=slowmode)
            return await ctx.send(f'Set the slowmode delay for channel {name.name} to {slowmode} seconds')

    @commands.command(brief='Creates a category')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def createcategory(self, ctx, *, name):
        guild = ctx.message.guild
        await guild.create_category(name)
        return await ctx.send(f'Created category {name}')

    # allows server members to set channel for welcome messages to send to
    @commands.command(brief='Sets the channel for welcome messages')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx):
        with open("guild.json", "r") as f:
            guildInfo = json.load(f)
            f.close()
    # sets channel to send message to as the channel the command was sent to
        guildInfo[ctx.message.guild.id] = ctx.message.channel.id

        with open("guild.json", "w") as f:
            try:
                json.dump(guildInfo, f)
            except:
                pass
            f.close()
        return await ctx.send('Channel set to: '+str(ctx.message.channel.id))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # role = discord.utils.get(member.server.roles, name='Member')
        # await client.add_roles(member, role)
        # if str(member.name) == 'zero0two2':
        #     Muted = get(member.guild.roles, name='Muted')
        #     u = member.guild.get_member(member.id)
        #     await u.add_roles(Muted)
        embed = discord.Embed(
            title='Welcome to ' + str(member.guild.name) + " " + str(member.display_name), color=random.randint(0, 0xffffff))

        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()

        with open("guild.json", "r") as f:
            guildInfo = json.load(f)
            f.close()
        channel = guildInfo[str(member.guild.id)]
        channel = self.bot.get_channel(channel)
        return await channel.send(embed=embed)

    # @bot.event
    # async def on_member_join(member):
    #     channel = bot.get_channel(751137949420224645)
    #     await channel.send(member.mention + " has entered!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(title=member.display_name + ' ('+str(member)+') has left ' +
                              str(member.guild.name), color=random.randint(0, 0xffffff))
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()

        with open("guild.json", "r") as f:
            guildInfo = json.load(f)
            f.close()
        channel = guildInfo[str(member.guild.id)]
        channel = self.bot.get_channel(channel)
        return await channel.send(embed=embed)

    @commands.command(brief='Deletes Kookies\' messages after a certain amount of seconds')
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def prune(self, ctx, time = None):
        with open('config.json', 'r') as config:
            info = json.load(config)
            config.close()
        id = str(ctx.guild.id)
        if id not in info:
            info[id] = {'prune': True, 'time': 60}
        else:
            if info[id]['prune']:
                info[id]['prune'] = False
            else:
                info[id]['prune'] = True
        if time == None:
            pass
        else:
            info[id]['time'] = int(time)
            
        with open('config.json', 'w') as config:
            json.dump(info, config)
            config.close()
        time = info[id]['time']
        if info[id]['prune']:
            message = 'Kookies\' responses will now be deleted after '+ str(time) + ' seconds'
        else:
            message = 'Pruning is now off'
        return await ctx.send(message)

def setup(bot):
    bot.add_cog(server(bot))
