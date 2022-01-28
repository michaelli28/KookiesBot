import sys
import urllib
import json
import datetime
import discord
import requests
from time import time
import markovify
from discord.ext import commands
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.utils import get
import discord.utils
from discord import Embed
from typing import Optional
import random
from pytz import timezone
import ksoftapi
import asyncio
from discord.ext import tasks
from operator import itemgetter
from discord.ext.commands.errors import BadArgument
import nltk
import io
from googletrans import Translator, LANGUAGES
from pathlib import Path
from subprocess import Popen
# nltk.download('wordnet')
from nltk.corpus import wordnet
import math
import multiprocessing
import psutil
from collections import Counter
import platform
kclient = ksoftapi.Client('1931343e09f8c6434c51af90c3a602ac06c29211')

from urllib.request import urlopen
from urllib.parse import quote as urlquote

UD_DEFINE_URL = 'https://api.urbandictionary.com/v0/define?term='



class UrbanDefinition(object):
    def __init__(self, word, definition, example, upvotes, downvotes):
        self.word = word
        self.definition = definition
        self.example = example
        self.upvotes = upvotes
        self.downvotes = downvotes

    def __str__(self):
        return '%s: %s%s (%d, %d)' % (
            self.word,
            self.definition[:50],
            '...' if len(self.definition) > 50 else '',
            self.upvotes,
            self.downvotes
        )

def _get_urban_json(url):
    f = urlopen(url)
    data = json.loads(f.read().decode('utf-8'))
    f.close()
    return data


def _parse_urban_json(json, check_result=True):
    result = []
    if json is None or any(e in json for e in ('error', 'errors')):
        print('UD: Invalid input for Urban Dictionary API')
    if check_result and ('list' not in json or len(json['list']) == 0):
        return result
    for definition in json['list']:
        d = UrbanDefinition(
            definition['word'],
            definition['definition'],
            definition['example'],
            int(definition['thumbs_up']),
            int(definition['thumbs_down'])
        )
        result.append(d)
    return result


def define(term):
    """Search for term/phrase and return list of UrbanDefinition objects.
    Keyword arguments:
    term -- term or phrase to search for (str)
    """
    json = _get_urban_json(UD_DEFINE_URL + urlquote(term))
    return _parse_urban_json(json)



with open('config.json', 'r') as config:
        configfile = json.load(config)
        config.close()
cooldown = int(configfile['cooldown'])
times = int(configfile['numberoftimes'])

class util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = bot.client
        self.trans = Translator()
        self.kclient = kclient

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = self.bot.get_guild(765941083254947911) #log guild
        if message.guild == guild:
            return
        channel = guild.get_channel(765941083254947914)


        if message.author.id != self.bot.user.id:
            try:
                if message.content != "":
                    embed = discord.Embed(color=random.randint(
                        0, 0xffffff), description=f'Message sent by {message.author.mention} in {message.channel.mention} in {message.guild.name} [Jump to Message]({message.jump_url})')
                    embed.add_field(name=f'{message.content}', value=f'\u200B')
                    if message.author.avatar != None:
                        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
                    else: 
                        embed.set_author(name=message.author.display_name)
                    embed.timestamp = datetime.datetime.utcnow()
                    await channel.send(embed=embed)

            except discord.errors.HTTPException:
                # if message.attachments:
                #     embed = discord.Embed(color=random.randint(
                #         0, 0xffffff), description=f'Message sent by {message.author.mention} in {message.channel.mention} in {message.guild.name} [Jump to Message]({message.jump_url})')
                #     for attachment in message.attachments:
                #         new = await attachment.to_file()
                #         await channel.send(file=new)
                #         embed.set_image(url=f'{attachment.url}')

                #     embed.set_author(name=message.author.display_name,
                #                         icon_url=message.author.avatar.url)
                #     embed.timestamp = datetime.datetime.utcnow()
                #     await channel.send(embed=embed)
                now = datetime.datetime.utcnow()
                current_time = now.strftime("%H:%M|%m/%d/%Y")
                await channel.send(f"Message sent in {message.guild} in {message.channel} by {message.author} at {current_time}  >  {message.jump_url}")
                if message.content != "":
                    await channel.send(message.content)
                if message.embeds:
                    await channel.send(message.embeds[0].to_dict())
                
            if message.attachments:
                for attachment in message.attachments:
                    new = await attachment.to_file()
                    await channel.send(attachment.url)
                    await channel.send(file=new)
            if message.embeds:
                for embed in message.embeds:
                    await channel.send(embed=embed)
        return

    @commands.command(brief="Invites a user, only works if the user shares another guild with the bot", aliases=["invite","invitemember","memberinvite","userinvite","sendinvite",])
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def inviteuser(self, ctx, *, user: discord.User):
        if user in ctx.guild.members:
            return await ctx.send(f"{user} is already in this guild")
        link = await ctx.channel.create_invite(max_uses = 1)
        try:
            await user.send(f"You were invited to the server {ctx.guild.name} by {ctx.author.name}")
            await ctx.send(f"{user.mention} was invited to the server")
            return await user.send(link)
        except:
            return await ctx.send(f"I was unable to send an invite link to {user.name}, check if they have allowed messages from everyone")

    @commands.command(name='textart', aliases=['coolfont'], brief='Makes text look cool (the font is a number from 1-12 and the color is a hexadecimal color')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def font_generator(self, ctx, font: str ='3', color: str = '00fffff', *, text: str = ""):
        """Generate cool font"""
        if not text:
            return await ctx.send('Please enter text :pager:')

        url = f'https://gdcolon.com/tools/gdfont/img/{text}?font={font}&color={color}'
        async with self.client.get(url) as r:
            if r.status != 200:
                return await ctx.send('API error, try again later')
            data = io.BytesIO(await r.read())
        return await ctx.send(file=discord.File(data, 'textart.png'))

    @commands.command(name='color', brief='Shows the color of a hex code')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def color(self, ctx, color=None):
        if color==None:
            return await ctx.send('Input a color')
        else:
            try:
                embed = discord.Embed(title=f'Color for **{color}**', color=int(color, 16))
            except ValueError:
                return await ctx.send('Invalid input for hexadecimal color')
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_author(name=ctx.author.display_name, url=ctx.author.avatar.url)
            return await ctx.send(embed=embed)

    @commands.command(aliases=['urbandictionary', 'urbandefine'], brief='Gives the definitions of a word using Urban Dictionary')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def urban(self, ctx, *, word):

        embeds = 0
        defs = define(word)
        number = len(defs)

        n=1
        des = ''
        toolong = False
        listEmbeds = []
        triggered = False
        async with ctx.typing():
            for definition in defs:

                words = f'**Definition {n})**\n{definition.definition}\n'
                n += 1
                test = des + words
                if len(test) > 2048:
                    toolong = True
                    embeds+=1
                    if not triggered:
                        triggered = True
                elif int(n) == int(number+1):

                    embed = discord.Embed(title=f'Definition of `{word}`, Part {embeds}', description=des+words)
                    embed.set_author(name=ctx.author.display_name,
                                    icon_url=ctx.author.avatar.url)
                    embed.timestamp = datetime.datetime.utcnow()
                    listEmbeds.append(embed)
                if toolong:
                    embed = discord.Embed(title=f'Definition of `{word}`, Part {embeds}', description=des)
                    embed.set_author(name=ctx.author.display_name,
                                    icon_url=ctx.author.avatar.url)
                    embed.timestamp = datetime.datetime.utcnow()
                    listEmbeds.append(embed)
                    des = ''
                    des += words
                    toolong = False
                    if n==number+1:
                        embeds+=1
                        embed = discord.Embed(title=f'Definition of `{word}`, Part {embeds}', description=des)
                        embed.set_author(name=ctx.author.display_name,
                                        icon_url=ctx.author.avatar.url)
                        embed.timestamp = datetime.datetime.utcnow()
                        listEmbeds.append(embed)
                else:
                    des += words
            if not triggered:
                embed = discord.Embed(title=f'Definition of `{word}`', description=des)
                embed.set_author(name=ctx.author.display_name,
                                icon_url=ctx.author.avatar.url)
                embed.timestamp = datetime.datetime.utcnow()
                return await ctx.send(embed=embed)
            else:
                for embed in listEmbeds:
                    await ctx.send(embed=embed)
                return
    @commands.command(aliases=['def'], brief='Gives the definitions of a word using a module')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def define(self, ctx, *, word):
        synsets = wordnet.synsets(word)
        embed = discord.Embed(title=f'Definition of the word: `{word}`')
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        n = 1
        if len(synsets) == 0:
            return await ctx.send(f'No definitions found for `{word}`')
        else:
            pass
        for synset in synsets:
            definition = synset.definition()
            lists = '`'
            for hyp in synset.hypernyms():
                list = hyp.name().split('.')
                hypernym = list[0]
                lists += hypernym
                lists += '`\n`'
            lists = lists[:-1]
            embed.add_field(name=f'Definition {n})',
                            value=definition + '\nHypernym(s):\n' + lists, inline=False)
            n+=1
        return await ctx.send(embed=embed)
    @commands.command(brief='Get your ping')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def ping(self, ctx):
        start = time()
        message = await ctx.send(f"Pong! Latency: {self.bot.latency*1000:,.0f} ms.")
        end = time()

        return await message.edit(content=f"Pong! Latency: {self.bot.latency*1000:,.0f} ms. Response time: {(end-start)*1000:,.0f} ms")

    @commands.command(brief='Gets the time')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def time(self, ctx):
        now = datetime.datetime.utcnow()
        current_time = now.strftime("%H:%M:%S")

        return await ctx.send(current_time)

    @commands.command(brief='Get your id')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def id(self, ctx):
        author = ctx.message.author.id
        return await ctx.send(author)

    @commands.command(aliases=['sa', 'av', 'avatar', 'pfp'], brief='Send a picture of someones avatar')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def stealavatar(self, ctx, *, member: discord.Member=None):
        member = member or ctx.author
        embed = discord.Embed(title=f'{member.name}\'s avatar', color=random.randint(
            0, 0xffffff), url=f'{member.avatar.url}')
        embed.set_image(url=member.avatar.url)
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)
        # ext = 'gif' if user.is_avatar_animated() else 'png'
        # await ctx.send(file=discord.File(BytesIO(await user.avatar.url.read()), f"{user.id}.{ext}"))

    @commands.command(name='serverinfo', aliases=['server', 'sinfo'], brief='Gets info about the server')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def serverinfo(self, ctx, *, name: str = ""):
        """Get server info"""
        if name:
            server = None
            try:
                server = self.bot.get_guild(int(name))
                if not server:
                    return await ctx.send('Server not found :satellite_orbital:')
            except:
                for i in self.bot.guilds:
                    if i.name.lower() == name.lower():
                        server = i
                        break
                if not server:
                    return await ctx.send("Server not found :satellite_orbital: or maybe I'm not in it")
        else:
            server = ctx.guild
        # Count online members
        online = 0
        for i in server.members:
            if str(i.status) == 'online' or str(i.status) == 'idle' or str(i.status) == 'dnd':
                online += 1
        # Count channels
        tchannel_count = len(
            [x for x in server.channels if type(x) == discord.channel.TextChannel])
        vchannel_count = len(
            [x for x in server.channels if type(x) == discord.channel.VoiceChannel])
        # Count roles
        role_count = len(server.roles)

        # Create embed
        em = discord.Embed(color=0x00CC99)
        em.set_author(name='Server Info:', icon_url=server.owner.avatar.url)
        em.add_field(name='Name', value=f'{server.name}')
        em.add_field(name='Owner', value=f'{server.owner}', inline=False)
        em.add_field(name='Members', value=f'{server.member_count}')
        em.add_field(name='Online', value=f'{online}')
        em.add_field(name='Region', value=f'{str(server.region).title()}')
        em.add_field(name='Text Channels', value=f'{tchannel_count}')
        em.add_field(name='Voice Channels', value=f'{vchannel_count}')
        em.add_field(name='Verification Level',
                     value=f'{str(server.verification_level).title()}')
        em.add_field(name='Number of roles', value=f'{role_count}')
        em.add_field(name='Highest role', value=f'{server.roles[-1]}')
        em.add_field(
            name='Created At', value=f"{server.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S')}", inline=False)
        em.set_thumbnail(url=server.icon)
        em.set_footer(text='Server ID: %s' % server.id)
        em.set_author(name=ctx.author.display_name,
                      icon_url=ctx.author.avatar.url)
        em.timestamp = datetime.datetime.utcnow()

        return await ctx.send(embed=em)


    # @commands.command(name='url', aliases=['shorten'], brief='Shortens a url')
    # @commands.cooldown(times, cooldown, commands.BucketType.user)
    # async def url_shorten(self, ctx, *, url):
    #     if not url:
    #         return await ctx.send('Please specify the url :link:')
    #     if not url.startswith('http'):
    #         url = 'http://' + url
    #     try:
    #         async with ctx.typing():
    #             async with self.client.post('https://rel.ink/api/links/', data={'url': url}) as r:
    #                 data = await r.json()
    #         if data.get('hashid'):
    #             return await ctx.send(f"Url: `{data['url']}`\nShort: https://rel.ink/{data['hashid']}")
    #     except:
    #         return await ctx.send('Failed to shorten url :x:')


    @commands.command(name='botinfo', aliases=['info'], brief='Shows some info about the bot!')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def botinfo(self, ctx):
        channel_types = Counter(type(c) for c in self.bot.get_all_channels())
        voice = channel_types[discord.channel.VoiceChannel]
        text = channel_types[discord.channel.TextChannel]
        NotThatBot = self.bot.get_user(587068610237693963)
        # hurb = self.bot.get_user(630499390938808379)
        embed = discord.Embed(
            title="Bot Info:",
            description=(
                f"Member Count: **{len(self.bot.users)}**\n"
                f"Servers: **{len(self.bot.guilds)}**\n"
                f"Commands: **{len(self.bot.commands)}**\n"
                f"Text Channels: **{text}**\n"
                f"Voice Channels: **{voice}**\n"
                f"Discord.py Version: **{discord.__version__}**\n"
                f"Python Version: **{platform.python_version()}**\n"
                f"Server: **{platform.system()}**\n"
                f"Ping: **{round(self.bot.latency * 1000)}ms**\n"
                f"CPU Count: **{multiprocessing.cpu_count()}**\n"
                f"CPU Usage: **{psutil.cpu_percent()}%**\n"
                f"RAM: **{psutil.virtual_memory().percent}%**\n"
                f"Creator: **{str(NotThatBot)}**"
                # f"Creators: **{str(NotThatBot)}** and **{str(hurb)}**"
            ),
            color=random.randint(0,0xffffff))
        embed.set_author(name=ctx.guild.me.name, icon_url=ctx.guild.me.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()

        return await ctx.send(embed=embed)
    @commands.command(name='userinfo', aliases=['user', 'uinfo'], brief='Gets info about a user')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def userinfo(self, ctx, *, name=""):
        """Get user info. Ex: ;user @user"""
        if name:
            try:
                user = ctx.message.mentions[0]
            except IndexError:
                user = ctx.guild.get_member_named(name)
            try:
                if not user:
                    user = ctx.guild.get_member(int(name))
                if not user:
                    user = self.bot.get_user(int(name))
            except ValueError:
                pass
            if not user:
                await ctx.send('User not found :man_frowning_tone1:')
                return
        else:
            user = ctx.message.author

        if isinstance(user, discord.Member):
            role = user.top_role.name
            if role == "@everyone":
                role = "N/A"
            voice_state = None if not user.voice else user.voice.channel

        em = discord.Embed(color=random.randint(0,0xffffff))
        em.add_field(name='User ID', value=f'{user.id}')
        if isinstance(user, discord.Member):
            if isinstance(user.activity, discord.Spotify):
                activity = "Listening to " + user.activity.title
            elif user.activity is not None:
                activity = str(user.activity.type)[
                    13:].title() + ' ' + user.activity.name
            else:
                activity = None

            em.add_field(name='Nick', value=f'{user.nick}')
            em.add_field(name='Status', value=f'{user.status}')
            em.add_field(name='In Voice', value=f'{voice_state}')
            em.add_field(name='Activity', value=f'{activity}')

            em.add_field(name='Highest Role', value=f'{role}')

            rolesMsg = ''
            for role in user.roles:
                if role.name != '@everyone':
                    rolesMsg += str(role) + ', '
            if len(rolesMsg)>0:
                em.add_field(name='Roles', value=rolesMsg[:-2], inline=False)
            else:
                em.add_field(name='Roles', value='None', inline=False)

        em.add_field(name='Account Created',
                     value=f"{user.created_at.__format__('%A, %d %B %Y @ %H:%M:%S')}", inline=False)
        if isinstance(user, discord.Member):
            em.add_field(
                name='Join Date', value=f"{user.joined_at.__format__('%A, %d %B %Y @ %H:%M:%S')}", inline=False)
        em.set_thumbnail(url=user.avatar.url)
        em.set_author(name=user, icon_url=user.avatar.url)
        em.timestamp = datetime.datetime.utcnow()

        return await ctx.send(embed=em)

    @commands.command(name='restart')
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send("Restarting...")
        bot_folder=Path('/app')
        bot_file=bot_folder / "Kookies-bot"
        Popen("python "+str(bot_file))
        quit()

    # @commands.command(name='convert', aliases=['currency'], description = 'Converts currency')
    # @commands.cooldown(times, cooldown, commands.BucketType.user)
    # async def currency(self, ctx, value: str="", _from: str="", to: str=""):
    #     """Currency conversion"""
    #     if value=="" or _from=="" or to=="":
    #         return await ctx.send("Please enter values in proper format\n`~convert [value] [from] [to]`\neg: `~convert 16 usd inr`")

    #     try:
    #         async with ctx.typing():
    #             c = await self.kclient.kumo.currency_conversion(_from, to, value)
    #     except (ksoftapi.NoResults, ksoftapi.errors.APIError):
    #         await ctx.send('Conversion Failed :x:')
    #     else:
    #         await ctx.send(f":currency_exchange: Conversion:\n`{value} {_from.upper()}` = `{c.pretty}`")


    # @commands.command(name='trace', aliases=['ip'], brief='Traces your ip')
    # @commands.cooldown(times, cooldown, commands.BucketType.user)
    # async def trace(self, ctx, *, ip: str = ""):
    #     """Trace ip"""
    #     if ip == "":
    #         return await ctx.send("Please enter an `IP` address :satellite:")

    #     try:
    #         async with ctx.typing():
    #             info = await self.kclient.kumo.trace_ip(ip)
    #     except (ksoftapi.NoResults, ksoftapi.errors.APIError):
    #         return await ctx.send('Unable to locate :x:\nEnter valid IP')
    #     else:
    #         details = [['City', 'city'], ['Continent code', 'continent_code'], ['Continent name', 'continent_name'], ['Country code', 'country_code'], ['Country_name', 'country_name'], [
    #             'DMA code', 'dma_code'], ['Latitude', 'latitude'], ['Longitude', 'longitude'], ['Postal code', 'postal_code'], ['Region', 'region'], ['Timezone', 'time_zone']]
    #         description = []
    #         for i in details:
    #             description.append(f'{i[0]}: `{getattr(info, i[1])}`')
    #         description.append(f':map:Map: [GoogleMaps]({info.gmap})')

    #         embed = discord.Embed(title=":satellite_orbital: IP information:", color=random.randint(0,0xffffff), description="\n".join(description))
    #         embed.set_footer(text=ip, icon_url=ctx.author.avatar.url)
    #         embed.set_author(name=ctx.author.display_name,
    #                          icon_url=ctx.author.avatar.url)
    #         embed.timestamp = datetime.datetime.utcnow()
    #         return await ctx.send(embed=embed)

    @commands.command(name='translate', brief='Translates text, use --list to see list of languages')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def translate(self, ctx, *args):
        """Translator"""
        if len(args) > 0:
            if args[0] == '--list':
                lang = ''
                for l in LANGUAGES:
                    lang = lang+str(l)+' ('+str(LANGUAGES[l]).title()+')\n'
                embed = discord.Embed(title='List of supported languages', description=str(
                    lang), color=discord.Color(0x5DADEC))
                await ctx.send(embed=embed)
            elif len(args) > 1:
                destination = args[0]
                try:
                    toTrans = ' '.join(args[1:len(args)])
                except IndexError:
                    await ctx.send('Input text to translate')
                try:
                    async with ctx.typing():
                        translation = self.trans.translate(toTrans, dest=destination)
                    embed = discord.Embed(description=translation.text,
                                            color=random.randint(0,0xffffff))
                    embed.set_author(name=ctx.author.display_name,
                        icon_url=ctx.author.avatar.url)
                    embed.timestamp = datetime.datetime.utcnow()
                    embed.set_footer(
                        text=f'Translated {LANGUAGES[translation.src]} to {LANGUAGES[translation.dest]}.', icon_url='https://i.ibb.co/1np1s8P/translate.png')
                    await ctx.send(embed=embed)
                except: #Exception as e:
                    return await ctx.send('Unable to translate :x:\nMaybe language id was wrong')
            else:
                return await ctx.send(content='Please add a language id\nType `;translate --list` for the list')
        else:
            return await ctx.send(content='Please add translations\neg.`;translate en Hola`\nType `;translate --list` for supported languages')

def setup(bot):
	bot.add_cog(util(bot))
