import inspect
from contextlib import redirect_stdout
import aiohttp
import traceback
import textwrap
import io
import ast
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.menus import MenuPages, ListPageSource
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
import requests
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
import textwrap
import traceback
import aiohttp
from contextlib import redirect_stdout
from textwrap import TextWrapper




class misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = bot.client
        self.message = None
        self.ctx = None
    @commands.command(name='repeat', brief='Repeats your input')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def do_repeat(self, ctx, *, inp: str):
        """A simple command which repeats your input!
        Parameters
        ------------
        inp: str
            The input you wish to repeat.
        """
        self.ctx = ctx
        self.message = inp
        message = ctx.message
        await message.delete()
        return await ctx.send(inp)

    @do_repeat.error
    async def do_repeat_handler(self, ctx, error):
        """A local Error Handler for our command do_repeat.
        This will only listen for errors in do_repeat.
        The global on_command_error will still be invoked after.
        """

        # Check if our required argument inp is missing.
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'inp':
                return await ctx.send("You forgot to give me input to repeat!")

    @commands.command(name='snipe', brief='Snipes the last repeat command')
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.default)
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
            for i in range(times):
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
            return await ctx.message.add_reaction('\u2049')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    try:
                        out = await ctx.send(f'```py\n{value}\n```')
                    except:
                        paginated_text = paginate(value)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                out = await ctx.send(f'```py\n{page}\n```')
                                break
                            await ctx.send(f'```py\n{page}\n```')
            else:
                try:
                    out = await ctx.send(f'```py\n{value}{ret}\n```')
                except:
                    paginated_text = paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f'```py\n{page}\n```')
                            break
                        await ctx.send(f'```py\n{page}\n```')

        if out:
            await ctx.message.add_reaction('\u2705')  # tick
        elif err:
            await ctx.message.add_reaction('\u2049')  # x
        else:
            await ctx.message.add_reaction('\u2705')
        return

    @commands.command(name='ascii', brief='Ascii art of avatar or image')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ascii(self, ctx, image_link: str=""):
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
        n = ascii_file.write(result)
        ascii_file.close()

        file = discord.File('ascii.txt')
        em = discord.Embed(color=discord.Colour(0xFFFF66))
        em.set_thumbnail(url=image_link)
        return await ctx.send(file=file, embed=em)



    @commands.command(name='advice', brief='Generates advice')
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rhyme(self, ctx, word=""):
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
    @commands.cooldown(1, 5, commands.BucketType.user)
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
