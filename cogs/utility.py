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
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
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
# nltk.download('wordnet')
from nltk.corpus import wordnet
kclient = ksoftapi.Client('eyJ0IjogImFwcCIsICJrIjogImtobWFjc2lnIiwgInBrIjogbnVsbCwgIm8iOiAiNTg3MDY4NjEwMjM3NjkzOTYzIiwgImMiOiA3NTczNDQ4fQ.bdb3a6d6f99d566327126abc55fdbd969b04c877ccd7cd5c5df316a343e80355')

class util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = bot.client
        self.trans = Translator()
        self.kclient = kclient

    @commands.command(name='textart', aliases=['coolfont'], brief='Makes text look cool')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def font_generator(self, ctx, font='3', color = '00fffff', *, text: str = ""):
        """Generate cool font"""
        if not text:
            return await ctx.send('Please enter text :pager:')

        url = f'https://gdcolon.com/tools/gdfont/img/{text}?font={font}&color={color}'
        async with self.client.get(url) as r:
            if r.status != 200:
                return await ctx.send('API error, try again later')
            data = io.BytesIO(await r.read())
        return await ctx.send(file=discord.File(data, 'textart.png'))

    @commands.command(aliases=['def'], brief='Gives the definitions of a word without using an API')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def define(self, ctx, *, word):
        synsets = wordnet.synsets(word)
        embed = discord.Embed(title=f'Definition of the word: `{word}`')
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
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

    @commands.command(brief='Get your ping')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx):
        start = time()
        message = await ctx.send(f"Pong! Latency: {self.bot.latency*1000:,.0f} ms.")
        end = time()

        return await message.edit(content=f"Pong! Latency: {self.bot.latency*1000:,.0f} ms. Response time: {(end-start)*1000:,.0f} ms")

    @commands.command(brief='Gets the time')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def time(self, ctx):
        now = datetime.datetime.utcnow()
        current_time = now.strftime("%H:%M:%S")

        return await ctx.send(current_time)

    @commands.command(brief='Get your id')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def id(self, ctx):
        author = ctx.message.author.id
        return await ctx.send(author)

    @commands.command(aliases=['sa'], brief='Send a picture of someones avatar')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stealavatar(self, ctx, *, member: discord.Member):
        embed = discord.Embed(title=f'{member.name}\'s avatar', color=random.randint(
            0, 0xffffff), url=f'{member.avatar_url}')
        embed.set_image(url=member.avatar_url)
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)

    @commands.command(name='serverinfo', aliases=['server', 'sinfo'], brief='Gets info about the server')
    @commands.cooldown(1, 5, commands.BucketType.user)
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
        em.set_author(name='Server Info:', icon_url=server.owner.avatar_url)
        em.add_field(name='Name', value=f'`{server.name}`')
        em.add_field(name='Owner', value=f'`{server.owner}`', inline=False)
        em.add_field(name='Members', value=f'`{server.member_count}`')
        em.add_field(name='Online', value=f'`{online}`')
        em.add_field(name='Region', value=f'`{str(server.region).title()}`')
        em.add_field(name='Text Channels', value=f'`{tchannel_count}`')
        em.add_field(name='Voice Channels', value=f'`{vchannel_count}`')
        em.add_field(name='Verification Level',
                     value=f'`{str(server.verification_level).title()}`')
        em.add_field(name='Number of roles', value=f'`{role_count}`')
        em.add_field(name='Highest role', value=f'`{server.roles[-1]}`')
        em.add_field(
            name='Created At', value=f"`{server.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S')}`", inline=False)
        em.set_thumbnail(url=server.icon_url)
        em.set_footer(text='Server ID: %s' % server.id)
        em.set_author(name=ctx.author.display_name,
                      icon_url=ctx.author.avatar_url)
        em.timestamp = datetime.datetime.utcnow()

        return await ctx.send(embed=em)


    @commands.command(name='url', aliases=['shorten'], brief='Shortens a url')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def url_shorten(self, ctx, *, url):
        if not url:
            return await ctx.send('Please specify the url :link:')
        if not url.startswith('http'):
            url = 'http://' + url
        try:
            async with ctx.typing():
                async with self.client.post('https://rel.ink/api/links/', data={'url': url}) as r:
                    data = await r.json()
            if data.get('hashid'):
                return await ctx.send(f"Url: `{data['url']}`\nShort: https://rel.ink/{data['hashid']}")
        except:
            return await ctx.send('Failed to shorten url :x:')

    @commands.command(name='userinfo', aliases=['user', 'uinfo', 'ui'], brief='Gets info about a user')
    @commands.cooldown(1, 5, commands.BucketType.user)
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

        em = discord.Embed(colour=0x00CC99)
        em.add_field(name='User ID', value=f'`{user.id}`')
        if isinstance(user, discord.Member):
            if isinstance(user.activity, discord.Spotify):
                activity = "Listening " + user.activity.title
            elif user.activity is not None:
                activity = str(user.activity.type)[
                    13:].title() + ' ' + user.activity.name
            else:
                activity = None

            em.add_field(name='Nick', value=f'`{user.nick}`')
            em.add_field(name='Status', value=f'`{user.status}`')
            em.add_field(name='In Voice', value=f'`{voice_state}`')
            em.add_field(name='Activity', value=f'`{activity}`')
            em.add_field(name='Highest Role', value=f'`{role}`')
        em.add_field(name='Account Created',
                     value=f"`{user.created_at.__format__('%A, %d %B %Y @ %H:%M:%S')}`", inline=False)
        if isinstance(user, discord.Member):
            em.add_field(
                name='Join Date', value=f"`{user.joined_at.__format__('%A, %d %B %Y @ %H:%M:%S')}`", inline=False)
        em.set_thumbnail(url=user.avatar_url)
        em.set_author(name=user, icon_url=user.avatar_url)
        em.timestamp = datetime.datetime.utcnow()

        return await ctx.send(embed=em)

    @commands.command(name='trace', aliases=['ip'], brief='Traces your ip')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def trace(self, ctx, ip: str = ""):
        """Trace ip"""
        if ip == "":
            return await ctx.send("Please enter an `IP` address :satellite:")

        try:
            async with ctx.typing():
                info = await self.kclient.kumo.trace_ip(ip)
        except (ksoftapi.NoResults, ksoftapi.errors.APIError):
            return await ctx.send('Unable to locate :x:\nEnter valid IP')
        else:
            details = [['City', 'city'], ['Continent code', 'continent_code'], ['Continent name', 'continent_name'], ['Country code', 'country_code'], ['Country_name', 'country_name'], [
                'DMA code', 'dma_code'], ['Latitude', 'latitude'], ['Longitude', 'longitude'], ['Postal code', 'postal_code'], ['Region', 'region'], ['Timezone', 'time_zone']]
            description = []
            for i in details:
                description.append(f'{i[0]}: `{getattr(info, i[1])}`')
            description.append(f':map:Map: [GoogleMaps]({info.gmap})')

            embed = discord.Embed(title=":satellite_orbital: IP information:", color=random.randint(0,0xffffff), description="\n".join(description))
            embed.set_footer(text=ip, icon_url=ctx.author.avatar_url)
            embed.set_author(name=ctx.author.display_name,
                             icon_url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=embed)

    @commands.command(name='translate', brief='Translates text, use --list to see list of languages')
    @commands.cooldown(1, 5, commands.BucketType.user)
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
                        icon_url=ctx.author.avatar_url)
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
