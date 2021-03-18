import inspect
from contextlib import redirect_stdout
import aiohttp
import traceback
import textwrap
import io
import ast
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
import ctypes
import requests
import os
import re
import time
from collections import Counter
import asyncio
from discord.ext import tasks
from pytz import timezone
from discord.ext.commands.errors import BadArgument
from time import time
import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet
import ksoftapi
import inspect
import urllib
import io
import gtts
import textwrap
import traceback
import time
import sys
import aiohttp
from contextlib import redirect_stdout
from textwrap import TextWrapper

with open('config.json', 'r') as config:
        configfile = json.load(config)
        config.close()
cooldown = int(configfile['cooldown'])
times = int(configfile['numberoftimes'])



class misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = bot.client
        self.message = None
        self.ctx = None
        self.lang = {}
        self.channels = {}
    @commands.command(aliases=['botinvite'], brief='Sends an invite link')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def invite(self, ctx):
        perms = discord.Permissions(administrator=True)
        return await ctx.send(f"Use this URL to invite me\n<{discord.utils.oauth_url(self.bot.user.id,permissions=perms)}>")

    async def _join(self, ctx: commands.Context):
        """Joins a voice channel"""
        #await ctx.message.delete()


        channel = ctx.author.voice.channel


        try:
            channel = await channel.connect()
            return channel
        except Exception as e:
            print(e)
            # await ctx.send('The bot seems to be in a voice channel although this might not always be the case (it was kicked out) or it is playing music in which case tts won\'t work')
            return None
        

    @commands.command(aliases=['talk'], brief='Speaks a message into the voice channel that you are in')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def tts(self, ctx, *, text: str):
        voiceconnect = get(ctx.bot.voice_clients, guild=ctx.guild)
        if not voiceconnect or not voiceconnect.is_connected():
            channel = await self._join(ctx)
            if channel:
                self.channels[ctx.guild.id] = channel
        else:
            try:
                channel = self.channels[ctx.guild.id]
            except KeyError:
                await ctx.send(self.channels)
                return await ctx.send('The bot seems to have joined the voice channel via a music command, do ;stop to remove the bot from the channel. Then use the tts command again to get the bot to rejoin')

        if not channel:
            return await ctx.send('The bot may be in voice channel from music commands, at this moment, there is no way to fix this if bot isn\'t ACTUALLY in a voice channel')

            
        # if not ctx.author.voice.channel or ctx.author.voice.channel != channel.channel:
        #     return await ctx.send('Join the same channel as the bot')
        if channel.is_playing():
            return await ctx.send(f'{ctx.author.mention}, the bot is currently speaking, please wait until it is finished')
        try:
            lang = self.lang[ctx.guild.id]
        except KeyError:
            self.lang[ctx.guild.id] = 'en-us'
            lang = 'en-us'
            
        speech = gtts.gTTS(text, lang=f"{lang}")
        speech.save('tts.mp3')

        channel.play(discord.FFmpegOpusAudio("tts.mp3"))
        return
        # if os.path.exists("tts.mp3"):
        #     os.remove("tts.mp3")
        # return
        # obj = io.BytesIO()
        # speech.write_to_fp(obj)
        # obj.seek(0)
        # return await ctx.send(discord.File(obj, "tts.mp3"))

    @commands.command(brief='Changes the language of the tts, use list for language argument to get a list of languages (en-us is the default)')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def ttsset(self, ctx, language: str = None):
        if language == 'list':
            string = ''

            for abb,lan in gtts.lang.tts_langs().items():
                add = f'{abb} ({lan})\n'
                string+=add

            embed = discord.Embed(title='List of Available Languages', color = random.randint(0, 0xffffff), description = string)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=embed)

        elif language in gtts.lang.tts_langs():
            self.lang[ctx.guild.id] = language
            return await ctx.send(f'Set the language of tts to {gtts.lang.tts_langs()[language]}')
        elif language == None:
            return await ctx.send(f'Current language is {self.lang[ctx.guild.id]} ({gtts.lang.tts_langs()[self.lang[ctx.guild.id]]})')

        else:
            string = ''

            for abb,lan in gtts.lang.tts_langs().items():
                add = f'{abb} ({lan})\n'
                string+=add

            embed = discord.Embed(title='List of Available Languages', color = random.randint(0, 0xffffff), description = string)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=embed)


    @commands.command(aliases=['stoptts'], brief='Ends the tts session by leaving the voice channel')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def ttsend(self, ctx):
        voiceconnect = get(ctx.bot.voice_clients, guild=ctx.guild)
        if not voiceconnect or not voiceconnect.is_connected():
            return await ctx.send('Not in a voice channel')
        else:
            await ctx.send('Stopping tts session, leaving voice channel')
            try:
                del self.channels[ctx.guild.id]
            except:
                pass
            return await voiceconnect.disconnect()

    @commands.command(name='repeat', brief='Repeats your input')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def do_repeat(self, ctx, *, inp: str):
        """A simple command which repeats your input!
        Parameters
        ------------
        inp: str
            The input you wish to repeat.
        """
        if ctx.message.content.find('@everyone') != -1:
            return await ctx.send('You can\'t ping spam here')
        if ctx.message.content.find('@here') != -1:
            return await ctx.send('You can\'t ping spam here')
        self.ctx = ctx
        self.message = inp
        message = ctx.message
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass
        return await ctx.send(inp)

    # @do_repeat.error
    # async def do_repeat_handler(self, ctx, error):
    #     """A local Error Handler for our command do_repeat.
    #     This will only listen for errors in do_repeat.
    #     The global on_command_error will still be invoked after.
    #     """

    #     # Check if our required argument inp is missing.
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         if error.param.name == 'inp':
    #             return await ctx.send("You forgot to give me input to repeat!")

    @commands.command(name='snipe', brief='Snipes the last repeat command')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def snipe(self, ctx):
        if self.ctx == None or self.message == None:
            return await ctx.send('No one has used the repeat command yet')
        else:
            embed = discord.Embed(title=f'{self.ctx.author.display_name} has been sniped by {ctx.author.display_name}', color=random.randint(0,0xffffff), description=f'{self.message}')
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_author(name=self.ctx.author.display_name,
                    icon_url=self.ctx.author.avatar_url)
            return await ctx.send(embed=embed)



    @commands.command(aliases=['sp'], brief='Spam a message a certain number of times, say stop or end or cancel to stop spam')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def spam(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send('How many times would you like to spam the message', delete_after=3)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            return await ctx.send('Please respond the number of times you would like to spam the message next time')
        try:
            times = int(msg.content)
            if times > 50 and str(ctx.author.id) != '587068610237693963':
                return await ctx.send('Number of messages is too high, ask owner')
        except:
            return await ctx.send('The number of times must be an integer')
        else:
            if times < 1:
                return await ctx.send('I can\'t send a message less than once!')
            for _ in range(times):
                await ctx.send(message)
            return await ctx.send('Done!', delete_after=2)


    @commands.command(name='eval', brief='Eval command')
    @commands.is_owner()
    async def _eval(self, ctx, *, body):
        """Evaluates python code"""
        env = {
            'ctx': ctx,
            'bot': self.bot,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'source': inspect.getsource
        }

        def cleanup_code(content):
            """Automatically removes code blocks from the code."""
            # remove ```py\n```
            if content.startswith('```') and content.endswith('```'):
                return '\n'.join(content.split('\n')[1:-1])

            # remove `foo`
            return content.strip('` \n')

        def get_syntax_error(e):
            if e.text is None:
                return f'```py\n{e.__class__.__name__}: {e}\n```'
            return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

        env.update(globals())

        body = cleanup_code(body)
        stdout = io.StringIO()
        err = out = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        def paginate(text: str):
            '''Simple generator that paginates text.'''
            last = 0
            pages = []
            for curr in range(0, len(text)):
                if curr % 1980 == 0:
                    pages.append(text[last:curr])
                    last = curr
                    appd_index = curr
            if appd_index != len(text)-1:
                pages.append(text[last:curr])
            return list(filter(lambda a: a != '', pages))

        try:
            exec(to_compile, env)
        except Exception as e:
            err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            return await ctx.message.add_reaction('\u2049') #error

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            # value = stdout.getvalue()
            err = await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        # else:
        #     value = stdout.getvalue()
        #     print(value)
        #     if ret is None:
        #         if value:
        #             try:
        #                 out = await ctx.send(f'```py\n{value}\n```')
        #             except:
        #                 paginated_text = paginate(value)
        #                 for page in paginated_text:
        #                     if page == paginated_text[-1]:
        #                         out = await ctx.send(f'```py\n{page}\n```')
        #                         break
        #                     await ctx.send(f'```py\n{page}\n```')
        #     else:
        #         try:
        #             out = await ctx.send(f'```py\n{value}{ret}\n```')
        #         except:
        #             paginated_text = paginate(f"{value}{ret}")
        #             for page in paginated_text:
        #                 if page == paginated_text[-1]:
        #                     out = await ctx.send(f'```py\n{page}\n```')
        #                     break
        #                 await ctx.send(f'```py\n{page}\n```')

        if out:
            await ctx.message.add_reaction('\u2705')  # tick
        elif err:
            await ctx.message.add_reaction('\u2049')  # x
        else:
            await ctx.message.add_reaction('\u2705')
        return

    @commands.command(name='botstop', aliases=['bstop'], brief='Shutdown the bot, NotThatBot#3360 only')
    @commands.is_owner()
    async def botstop(self, ctx):
        print('Goodbye')
        await ctx.send('Goodbye')
        await self.bot.logout()
        return

    @commands.command(brief='Adds an alias to an existing command')
    @commands.is_owner()
    async def alias(self, ctx, cmdname, alias):
        cmd = ctx.bot.get_command(cmdname)
        cmd.aliases.append(alias)
        # register the modified command
        ctx.bot.remove_command(cmdname)
        ctx.bot.add_command(cmd)
        return

    # @commands.command(name='reload')
    # @commands.is_owner()
    # async def reload_module(self, ctx, arg=None):
    #     """Reload module"""
    #     modules = ['musiclava', 'fun', 'utility', 'levels', 'CommandErrorHandler', 'misc', 'moderation', 'roles', 'school', 'server', 'games']
    #     if not arg:
    #         embed = discord.Embed(
    #             title='Modules', description='\n'.join(modules))
    #         embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    #         embed.timestamp = datetime.datetime.utcnow()
    #         return await ctx.send(embed=embed)
    #     if arg.lower() == 'all':
    #         for module in modules:
    #             msg = await ctx.send(f":arrows_counterclockwise: Reloading `{module}`...")
    #             try:
    #                 self.bot.unload_extension('cogs.' + module)
    #                 self.bot.load_extension('cogs.' + module)
    #             except:
    #                 await msg.edit(content=f":x: Reloading `{module}` Failed!")
    #             else:
    #                 await msg.edit(content=f":white_check_mark: Reloaded `{module}`")
    #     elif arg.lower() in modules:
    #         msg = await ctx.send(f":arrows_counterclockwise: Reloading `{arg.lower()}`...")
    #         try:
    #             self.bot.unload_extension('cogs.' + arg.lower())
    #             self.bot.load_extension('cogs.' + arg.lower())
    #         except:
    #             await msg.edit(content=f":x: Reloading `{arg.lower()}` Failed!")
    #         else:
    #             await msg.edit(content=f":white_check_mark: Reloaded `{arg.lower()}`")
    

    @commands.command(name='ascii', aliases=['ac'], brief='Ascii art of avatar or image')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def ascii(self, ctx, *, image_link: str=""):
        """Ascii art of avatar"""
        if not image_link:
            user = ctx.message.author
            image_link = user.avatar_url_as(size=1024)
        try:
            user = ctx.message.mentions[0]
            image_link = user.avatar_url_as(size=1024)
        except IndexError:
            pass
        try:
            result = requests.get(f'https://useless-api--vierofernando.repl.co/imagetoascii?image={image_link}').text.replace('<br>','\n')
        except:
            return await ctx.send("Failed :x:\nMaybe the url is wrong")

        ascii_file = open("ascii.txt", "w")
        # n = ascii_file.write(result)
        ascii_file.close()

        file = discord.File('ascii.txt')
        em = discord.Embed(color=discord.Colour(0xFFFF66))
        em.set_thumbnail(url=image_link)
        return await ctx.send(file=file, embed=em)


    @commands.command(name='advice', brief='Generates advice')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def advice(self, ctx):
        """Random Advice generator"""
        url = 'https://api.adviceslip.com/advice'
        async with ctx.typing():
            async with self.client.get(url) as r:
                if r.status != 200:
                    return ctx.send('API error, try again later')
                data = await r.json(content_type='text/html')

        return await ctx.send(data['slip']['advice'])

    @commands.command(name='rhyme', brief='Rhymes a word')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def rhyme(self, ctx, *, word=""):
        if not word:
            return await ctx.send("Specify a word :thought_balloon:")

        url = 'https://rhymebrain.com/talk'
        params = {'function': 'getRhymes',
                    'word': word.strip()}
        async with ctx.typing():
            async with self.client.get(url, params=params) as r:
                if r.status != 200:
                    return ctx.send('API error, try again later')
                data = await r.json()
            result = []
            for i in data[:30]:
                result.append(i['word'])
        return await ctx.send(f'Word(s) that rhyme with **{word}**\n' + f"`{', '.join(result)}`")

    @commands.command(brief='Gets news from CNN')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
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

def setup(bot):
    bot.add_cog(misc(bot))
