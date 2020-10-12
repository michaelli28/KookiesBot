import re
import math
import time
import httpx
import random
import discord
import asyncio
import datetime
import pyprog
import requests
import functools
import itertools
import youtube_dl
from time import sleep
from typing import Optional
from bs4 import BeautifulSoup
from async_timeout import timeout
from collections import OrderedDict
from discord.ext import commands,tasks


youtube_dl.utils.bug_reports_message = lambda: ''
global ido
global loop_value
global starttime
global counter
counter = 0
loop_value = 0
starttime = 0
ido = 0
class YTDLError(Exception):
    pass

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)
    ytdl.cache.remove()

    def __init__(self, ctx, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.50):
        super().__init__(source, volume)
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.duration_sec = data.get('duration')
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop: asyncio.BaseEventLoop = None, timestamp: int=0):
        loop = loop or asyncio.get_event_loop()
        ffmpeg_options = {
            'options': f'-vn -ss {timestamp}'
        }
        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                await ctx.send('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    await ctx.send('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))
        
        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @classmethod
    async def search_source(cls, bot: commands.Bot, ctx, search: str, *, loop: asyncio.BaseEventLoop = None, timestamp: int=0):
        channel = ctx.channel
        loop = loop or asyncio.get_event_loop()
        ffmpeg_options = {
            'options': f'-vn -ss {timestamp}'
        }
        cls.search_query = '%s%s:%s' % ('ytsearch', 10, ''.join(search))

        partial = functools.partial(cls.ytdl.extract_info, cls.search_query, download=False, process=False)
        info = await loop.run_in_executor(None, partial)

        cls.search = {}
        cls.search["title"] = f'Search results for:\n**{search}**'
        cls.search["type"] = 'rich'
        cls.search["color"] = 7506394
        cls.search["author"] = {'name': f'{ctx.author.name}', 'url': f'{ctx.author.avatar_url}', 'icon_url': f'{ctx.author.avatar_url}'}
        
        lst = []

        for e in info['entries']:
            #lst.append(f'`{info["entries"].index(e) + 1}.` {e.get("title")} **[{YTDLSource.parse_duration(int(e.get("duration")))}]**\n')
            VId = e.get('id')
            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
            lst.append(f'`{info["entries"].index(e) + 1}.` [{e.get("title")}]({VUrl})\n')

        lst.append('\nType a number to make a choice, Type *cancel* to exit')
        cls.search["description"] = "\n".join(lst)

        em = discord.Embed.from_dict(cls.search)
        await ctx.send(embed=em)

        def check(msg):
            return msg.content.isdigit() == True and msg.channel == channel or msg.content == 'cancel' or msg.content == 'Cancel'
        
        try:
            m = await bot.wait_for('message', check=check, timeout=45.0)

        except asyncio.TimeoutError:
            rtrn = 'timeout'

        else:
            if m.content.isdigit() == True:
                sel = int(m.content)
                if 0 < sel <= 10:
                    for key, value in info.items():
                        if key == 'entries':
                            """data = value[sel - 1]"""
                            VId = value[sel - 1]['id']
                            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
                            partial = functools.partial(cls.ytdl.extract_info, VUrl, download=False)
                            data = await loop.run_in_executor(None, partial)
                    rtrn = cls(ctx, discord.FFmpegPCMAudio(data['url'], **cls.FFMPEG_OPTIONS), data=data)
                else:
                    rtrn = 'sel_invalid'
            elif m.content == 'cancel':
                rtrn = 'cancel'
            else:
                rtrn = 'sel_invalid'
        
        return rtrn

    @staticmethod
    def parse_duration(duration: int):
        if duration > 0:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)

            duration = []
            if days > 0:
                duration.append('{}'.format(days))
            if hours > 0:
                if len(str(hours))==1:
                    hours = '0'+ str(hours)
                duration.append('{}'.format(hours))
            else:
                pass
            if minutes > 0:
                if len(str(minutes))==1:
                    minutes = '0'+ str(minutes)
                duration.append('{}'.format(minutes))
            else:
                duration.append('00')
            if seconds > 0:
                if len(str(seconds))==1:
                    seconds = '0'+ str(seconds)
                duration.append('{}'.format(seconds))
            else:
                duration.append('00')
            
            value = ':'.join(duration)
        
        elif duration == 0:
            value = "LIVE"
        
        return value










class VoiceError(Exception):
    pass


class Song:
    __slots__ = ('source', 'requester')
    
    def special_format(self,n):
        s, *d = str(n).partition(".")
        r = ",".join([s[x-3:x] for x in range(-3, -len(s), -3)][::-1] + [s[-3:]])
        return "".join([r] + d)

    def __init__(self, source: YTDLSource = None):
        self.source = source
        self.requester = source.requester
    
    def getsourceurl(self):
        return self.source.url

    def play_embed(self):
        embed = discord.Embed(title='Now playing', description='```fix\n{0.source.title}\n```'.format(self), color=discord.Colour.blue())
        if self.source.duration == 'LIVE':
            embed.add_field(name='Duration:', value=f'**```LIVE```**')
        else:
            embed.add_field(name='Duration:', value=f'**```0:00:0/{self.source.duration}```**')
            if loop_value == 0:
                embed.add_field(name='Looped:', value='**```False```**')
            elif loop_value == 1:
                embed.add_field(name='Looped:',value='**```True```**')
            if loop_value == 0:
                embed.add_field(name='Volume:', value=f'**```{self.source._volume*100}%```**')
            elif loop_value ==1:
                embed.add_field(name='Volume:', value=f'**```{self.source.volume*100}%```**')
        embed.add_field(name='Uploader:', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
        embed.add_field(name='Requested by:', value=self.requester.mention)
        embed.add_field(name='URL:', value='[Click]({0.source.url})'.format(self))
        if self.source.duration == 'LIVE':
            pass
        else:
            embed.add_field(name='Views:',value=f'```{self.special_format(self.source.views)}```',inline=False)
        embed.set_thumbnail(url=self.source.thumbnail)
        return embed

    def now_embed(self):
        global starttime
        current_time = time.time()
        difference = int(round(current_time - starttime))
        ido = str(datetime.timedelta(seconds=difference))
        embed = discord.Embed(title='Now playing', description='```fix\n{0.source.title}\n```'.format(self), color=discord.Colour.blue())
        if self.source.duration == 'LIVE':
            embed.add_field(name='Duration:', value=f'**```{self.source.duration}```**')
        else:    
            embed.add_field(name='Duration:', value=f'**```{ido}/{self.source.duration}```**')
            if loop_value == 0:
                embed.add_field(name='Looped:', value='**```False```**')
            elif loop_value == 1:
                embed.add_field(name='Looped:',value='**```True```**')
            if loop_value == 0:
                embed.add_field(name='Volume:', value=f'**```{self.source._volume*100}%```**')
            elif loop_value ==1:
                embed.add_field(name='Volume:', value=f'**```{self.source.volume*100}%```**')
        embed.add_field(name='Uploader:', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
        embed.add_field(name='Requested by:', value=self.requester.mention)
        embed.add_field(name='URL:', value='[Click]({0.source.url})'.format(self))
        if self.source.duration == 'LIVE':
            pass
        else:
            embed.add_field(name='Views:',value=f'```{self.special_format(self.source.views)}```',inline=False)
        embed.set_thumbnail(url=self.source.thumbnail)
        return embed



class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.song_history = []
        self.exists = True
        self._sendEmbed = True
        self._loop = False
        self._autoplay = True
        self._volume = 0.25
        self.skip_votes = set()
        self.msg = None
        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()
    @property
    def sendEmbed(self):
        return self._sendEmbed
    @sendEmbed.setter
    def sendEmbed(self, value: bool):
        self._sendEmbed = value
    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def autoplay(self):
        return self._autoplay

    @autoplay.setter
    def autoplay(self, value: bool):
        self._autoplay = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            global starttime
            global counter
            self.next.clear()
            self.now = None

            if self.loop == False:
                # If autoplay is turned on wait 15 seconds for a new song.
                # If no song is found find a new one,
                # else if autoplay is turned off try to get the
                # next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                # if self.autoplay and self.current:
                try:
                    async with timeout(15):
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    ctx = self._ctx
                    self.bot.loop.create_task(self.stop())
                    self.exists = False
                    embed = discord.Embed(color=discord.Colour.blue())
                    embed.add_field(name='Queue has ended', value='Leaving the voice channel')
                    return await ctx.send(embed=embed,delete_after=5)

                self.song_history.insert(0, self.current)
                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)

                if self.sendEmbed:
                    msg : discord.Message = await self.current.source.channel.send(embed=self.current.play_embed())
                    await msg.add_reaction('⏮️')
                    await msg.add_reaction('▶️')
                    await msg.add_reaction('⏸️')
                    await msg.add_reaction('🔁')
                    await msg.add_reaction('🔀')
                    await msg.add_reaction('⏭️')
                    await msg.add_reaction('➕')
                    await msg.add_reaction('➖')
                    starttime = 0
                    counter = 0
                    starttime = time.time()
                    self.msg = msg

                    


            #If the song is looped
            elif self.loop == True:
                self.song_history.insert(0, self.current)
                self.now = discord.FFmpegPCMAudio(
                    self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS)
                self.current.source.volume = self._volume
                # if ctx.voice_client:
                #     ctx.voice_client.source.volume = self._volume
                # ctx.voice_state.volume = self._volume
                self.voice.play(self.now, after=self.play_next_song)
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()
        try:
            await self.voice.disconnect()
        except:
            pass
        self.voice = None
















class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        self.svid = None

    def get_voice_state(self, ctx):
        state = self.voice_states.get(ctx.guild.id)
        if not state or not state.exists:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state
        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage(
                'This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx):
        ctx.voice_state = self.get_voice_state(ctx)
        self.vc = self.get_voice_state(ctx)




    #async def cog_command_error(self, ctx , error: commands.CommandError):
    #    await ctx.send('An error occurred: {}'.format(str(error)))
    #NOTE LOG----------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        now = datetime.datetime.now() 
        current_time = now.strftime("%H:%M|%m/%d/%Y")
        if message.author.id != self.bot.user.id:
            print(f"{message.guild}/{message.channel}/  {current_time}  /{message.author.name}>  {message.content}  ")

            #if message.embeds:
                #print(message.embeds[0].to_dict())

    @commands.command(name='join', aliases=['j'], brief='Makes the bot join a voice channel')
    async def _join(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Joins a voice channel"""
        #await ctx.message.delete()
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send('Specify a channel for me to join or join one')

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.send(f'Connected to: **{destination}**, type **-leave** to leave the channel')
            return
        ctx.voice_state.voice = await destination.connect()
        await ctx.send(f'Connected to: **{destination}**, type **-leave** to leave the channel')
    @commands.command(name='summon', brief='Summons the bot to a channel')
    async def _summon(self, ctx , *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel
        If no channel was specified, it joins your channel
        """
        #await ctx.message.delete()
        if not channel and not ctx.author.voice:
            raise VoiceError(
                'You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.send(f'Connected to: **{destination}** type **-leave** to leave the channel')
            return

        ctx.voice_state.voice = await destination.connect()
    
    @commands.command(name='leave', aliases=['disconnect', 'l'], brief='Makes the bot leave the channel it is in')
    async def _leave(self, ctx):
        """Clears the queue and leaves the voice channel"""
        #await ctx.message.delete()
        try:
            channel = ctx.author.voice.channel
        except:
            return await ctx.send('Join the voice channel that Kookies is in!')
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send('I am not currently in a voice channel!')

        await ctx.voice_state.stop()
        await ctx.send('Left **' + str(channel) + '**')
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume', aliases=['vol','v'], brief='Set the volume of the music')
    async def _volume(self, ctx, *, volume: int = None):
        """Sets the volume of the player"""

        if volume == None:
            try:
                return await ctx.send(f'Current volume is at **{ctx.voice_client.source.volume*100}**%')
            except:
                return await ctx.send(f'Current volume is at **{ctx.voice_state.volume*100}**%')
        if volume > 80:
            return await ctx.send("Volume exceeds 80 percent, safety implemented to reduce hearing loss")

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently in a voice channel')

        if 0 > volume > 80:
            return await ctx.send('Volume must be between 0 and 80')
        if ctx.voice_state.loop is True:
            ctx.voice_state._volume = volume/100
        else:
            if ctx.voice_client:
                ctx.voice_client.source.volume = volume/100
            ctx.voice_state.current.source.volume = volume/100
            ctx.voice_state.volume = volume/100
        await ctx.send('Volume of the player set to **{}**%'.format(volume))
    @commands.command()
    @commands.is_owner()
    async def voln(self, ctx, *, volume: int=None):

        if volume == None:
            return await ctx.send(f'Current volume is at **{ctx.voice_client.source.volume}%**')
        """Sets the volume of the player"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything')
        if 0 > volume > 100:
            return await ctx.send('Volume must be between 0 and 100')
        if ctx.voice_client:
            ctx.voice_client.source.volume = volume/100
        ctx.voice_state.volume = volume/100
        await ctx.send('Volume of the player set to **{}**%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing', 'np'], brief='Shows the song that is playing')
    async def _now(self, ctx):
        #await ctx.message.delete()
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!')
        await ctx.send(embed=ctx.voice_state.current.now_embed())
    
        """Displays the currently playing song"""
        '''
        # Create Object
        prog = pyprog.ProgressBar(" ", " ", total=ctx.voice_state.current.source.duration_sec, bar_length=ctx.voice_state.current.source.duration_sec, complete_symbol="●", not_complete_symbol="─", wrap_bar_prefix=" [", wrap_bar_suffix="] ", progress_explain="", progress_loc=pyprog.ProgressBar.PROGRESS_LOC_END)
        # Update Progress Bar
        prog.update()

        for i in range(ctx.voice_state.current.source.duration_sec):
            # Do something
            sleep(1)
            # Set current status
            prog.set_stat(i + 1)
            # Update Progress Bar again
            prog.update()
            await msg.edit(embed=ctx.voice_state.current.now_embed())
        # Make the Progress Bar final
        prog.end()
        '''
    @commands.command(name='pause', aliases=['pau'], brief='Pauses the song playing')
    async def _pause(self, ctx): 
        """Pauses the currently playing song"""
        #await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!')
        elif ctx.voice_state.is_playing:
            ctx.voice_state.voice.pause()
            embed = discord.Embed(title=f'{ctx.author.name} has paused the song!',color=discord.Colour.blue())
            await ctx.send(embed=embed,delete_after=5)


    @commands.command(name='resume', aliases=['re', 'res','r'], brief='Resumes the song')
    async def _resume(self, ctx ):
        """Resumes a currently paused song"""
        #await ctx.message.delete()
        vc = ctx.voice_client
        if not vc.is_playing:
            return await ctx.send('I am not currently playing anything!')
        if not vc.is_paused:
            return await ctx.send('Song is not paused')

        elif ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            vc.resume()
            embed = discord.Embed(title=f'{ctx.author.name} has resumed the song!',color=discord.Colour.blue())
            await ctx.send(embed=embed,delete_after=5)


    @commands.command(name='stop', brief='Stops the music, clears the queue, and disconnects the bot from the voice channel')
    async def _stop(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send('I am not currently in a voice channel!')
        await ctx.send('Are you sure you want to stop the song and delete queues and settings? Reply **y** for yes and **n** for no')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content.lower()=='y':
            await ctx.send('Stopping player and clearing queue')
        elif msg.content.lower()=='n':
            return await ctx.send('Continuing')
        else:
            return await ctx.send('Please reply with **y** or **n** next time, continuing')
        """Stops playing song and clears the queue"""
        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.pause()
        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]


        ctx.voice_state.songs.clear()
        '''
        if ctx.voice_state.autoplay:
            ctx.voice_state.autoplay = False
            await ctx.send('Autoplay is now turned off')
        '''


    @commands.command(name='skip', brief='Skips the song playing')
    async def _skip(self, ctx):
        #await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send('I am not currently in a voice channel!')
        if len(ctx.voice_state.songs) == 0: 
            if ctx.voice_state.autoplay:
                ctx.voice_state.skip()
                sembed = discord.Embed(title=f'{ctx.author.name} has skipped the song!',color=discord.Colour.blue())
                return await ctx.send(embed=sembed,delete_after=5)
            elif ctx.voice_state.loop:
                ctx.voice_state.skip()
                sembed = discord.Embed(title=f'{ctx.author.name} has skipped the song!',color=discord.Colour.blue())
                return await ctx.send(embed=sembed,delete_after=5)
            else: #not ctx.voice_state.loop and not ctx.voice_state.autoplay: 
                return await ctx.send('Empty queue, autoplay and loop not on, cannot skip the song')
        else:
            ctx.voice_state.skip()
            sembed = discord.Embed(title=f'{ctx.author.name} has skipped the song!',color=discord.Colour.blue())
            await ctx.send(embed=sembed,delete_after=5)

    @commands.command(name='queue', aliases=['check','q'], brief='Checks the queue for songs')
    async def _queue(self, ctx , *, page: int = 1):

        vc = ctx.voice_client

        if not vc or not vc.is_connected:
            return await ctx.send('I am not currently in a voice channel!')
        
        if len(ctx.voice_state.songs) == 0:
            emb=discord.Embed(title='Empty Queue',color=discord.Colour.blue())
            return await ctx.send(embed=emb,delete_after=5)

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page
        if page > pages:
            return await ctx.send('The page can\'t be larger than the number of pages')
        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '{0}. [{1.source.title}]({1.source.url})\n'.format(
                i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue),color=discord.Colour.blue())
                .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed,delete_after=10)


    @commands.command(name='shuffle', brief='Shuffles the queue')
    async def _shuffle(self, ctx):
        #await ctx.message.delete()
        vc = ctx.voice_client
        if not vc.is_playing:
            return await ctx.send('I am not currently playing anything!',delete_after=5)
        if len(ctx.voice_state.songs) == 0:
            emb=discord.Embed(title='Empty Queue',color=discord.Colour.blue())
            return await ctx.send(embed=emb,delete_after=5)
        ctx.voice_state.songs.shuffle()
        embed = discord.Embed(title=f'{ctx.author.name} has shuffled the queue')
        await ctx.send(embed=embed,delete_after=5)


    @commands.command(name='remove', brief='Removes a song from a queue')
    async def _remove(self, ctx , index: int):
        """Removes a song from the queue at a given index"""
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send('I am not currently in a voice channel!')
        if len(ctx.voice_state.songs) == 0:
            emb = discord.Embed(title='Empty Queue',color= discord.Colour.blue())
            return await ctx.send(embed=emb,delete_after=5)
        elif index > len(ctx.voice_state.songs):
            await ctx.send('Invalid index, number too large')
        else:
            ctx.voice_state.songs.remove(index - 1)
            await ctx.send('Removed song number **'+ str(index) + '**')

    @commands.command(name='loop', brief='Loops the song currently playing')
    async def _loop(self, ctx):
        """Loops the currently playing song
        Invoke this command again to unloop the song
        """
        #await ctx.message.delete()
        if not ctx.voice_state.is_playing:
            return await ctx.send('I am not currently playing anything')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.send('Song loop is now turned ' + ('**on**' if ctx.voice_state.loop else '**off**'))

    
    @commands.command(name='play', brief='Plays or queues a song or playlist by link or by search')
    async def _play(self, ctx, *, search: str=None):
        """Plays a song
        If there are songs in the queue, this will be queued until the
        other songs finished playing
        This command automatically searches from various sites if no URL is provided
        """
        if search == None:
            return await ctx.send('**You need to input a url or search**',delete_after=5)
        httpS = re.findall('www.',search)
        pList = re.findall('list=',search)
        indexL = re.findall('index=',search)
        watch = re.findall('watch',search)
        async with ctx.typing():
            if len(httpS)>0 and len(pList)>0:
                if len(indexL)==0 and len(watch)==0:
                    maxPlaylistSize = 120
                    showVidSize = None
                    # Spoof user agent to show whole page.
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'}
                    # Get the page
                    async with httpx.AsyncClient() as client:
                        response = await client.get(search, headers=headers)
                    playlist_urls = re.findall(
                        'watch\?v=(.*?)\\\\u0026list=', response.text)
                    if len(playlist_urls) >= maxPlaylistSize:
                        showVidSize = maxPlaylistSize
                    else:
                        showVidSize = len(playlist_urls)

                    try:
                        if not ctx.voice_state.voice:
                            await ctx.invoke(self._join)
                        await ctx.send('Putting songs into the queue, please wait a minute or two before checking the queue')
                        for n in range(showVidSize):
                            try:
                                source = await YTDLSource.create_source(ctx, 'https://www.youtube.com/watch?v=' + playlist_urls[n], loop=self.bot.loop)
                                song = Song(source)
                                await ctx.voice_state.songs.put(song)
                            except: 
                                await ctx.send('There was an error downloading ' + 'https://www.youtube.com/watch?v=' + playlist_urls[n])
                        return
                    except YTDLError as e:
                        await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                elif len(watch)>0:

                    response = requests.get(search)
                    soup = BeautifulSoup(response.text, 'lxml')

                    # print(soup.prettify())

                    playlistUrls = re.findall('"url":"/watch\?v=(.*?)"' , soup.prettify())
                    # print(playlistUrls)
                    playlistUrls2 = []

                    for url in playlistUrls:
                        url2 = re.findall('(.*?)\\\\u0026list=', url)
                        if len(url2)>0:
                            playlistUrls2.append(url2[0])
                        else:
                            playlistUrls2.append(url)
                    print(playlistUrls2)
                    # for i in range(len(playlistUrls2)):
                    #     if len(playlistUrls2[i][0]) > 3:
                    #         playlistUrls2.append(playlistUrls2[i][0])
                    #         playlistUrls2.remove(playlistUrls2[i])
                    # print(playlistUrls2)
                    res = [i for n, i in enumerate(playlistUrls2) if i not in playlistUrls2[:n]]
                    maxPlaylistSize = 120
                    showVidSize = None
                    print(res)
                    if len(res) >= maxPlaylistSize:
                        showVidSize = maxPlaylistSize
                    else:
                        showVidSize = len(res)
                    try:
                        if not ctx.voice_state.voice:
                            await ctx.invoke(self._join)
                        emb=discord.Embed(title='Enqueued playlist!',color=discord.Colour.blue())
                        await ctx.send(embed=emb)
                        await ctx.send('Putting songs into the queue, please wait a minute or two before checking the queue')
                        for n in range(showVidSize):
                            try:
                                source = await YTDLSource.create_source(ctx, 'https://www.youtube.com/watch?v=' + res[n], loop=self.bot.loop)
                                song = Song(source)
                                await ctx.voice_state.songs.put(song)
                            except:
                                # try:
                                #     source = await YTDLSource.create_source(ctx, 'https://www.youtube.com/watch?v=' + res[n][0], loop=self.bot.loop)
                                #     song = Song(source)
                                #     await ctx.voice_state.songs.put(song)

                                # except:
                                #     try:
                                await ctx.send('There was an error downloading ' + 'https://www.youtube.com/watch?v=' + res[n])
                                    # except:
                                    #     try:
                                    #         await ctx.send('There was an error downloading ' + 'https://www.youtube.com/watch?v=' + res[n])
                                    #     except:
                                    #         await ctx.send("There was an error downloading a song")
                        return
                    except YTDLError as e:
                        await ctx.send('An error occurred while processing this request: {}'.format(str(e)),delete_after=10)

            else:
                pass
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)),delete_after=10)
            else:
                if not ctx.voice_state.voice:
                    await ctx.invoke(self._join)
                try:
                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                except:
                    await ctx.send('There was an error downloading ' + song,delete_after=10)
                if ctx.voice_state.is_playing:
                    await ctx.send('Queued {}'.format(str(source)),delete_after=10)
                else:
                    await ctx.send('Playing {}'.format(str(source)),delete_after=10)

    @commands.command(name='seek', brief='Plays or queues a song or playlist by link or by search')
    async def seek(self, ctx, timestamp=0):
        source = await YTDLSource.create_source(ctx, Song.getsourceurl, loop=self.bot.loop, timestamp=timestamp)
        song = Song(source)
        await ctx.voice_state.songs.put(song)
        return await ctx.send(f'Seeking to {timestamp} seconds')


    @commands.command(name='history', aliases=['h','his'], brief='Shows the history of songs played')
    async def _history(self, ctx, *, page: int = 1):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!')
        
        if len(ctx.voice_state.song_history) == 0:
            emb=discord.Embed(title='Empty history',color=discord.Colour.blue())
            return await ctx.send(embed=emb)

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.song_history) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.song_history[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(color= discord.Colour.blue(),description='{} tracks:\n\n{}'.format(len(ctx.voice_state.song_history), queue))
                .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed,delete_after=10)
    
    @commands.command(name='search', brief='Shows 10 search results for videos')
    async def _search(self, ctx, *, search: str=None):


        if (search)==None:
            return await ctx.send('Input a search please',delete_after=5)
        async with ctx.typing():
            try:
                source = await YTDLSource.search_source(self.bot, ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)),delete_after=5)
            else:
                if source == 'sel_invalid':
                    await ctx.send('Invalid selection')
                elif source == 'cancel':
                    await ctx.send(':white_check_mark:')
                elif source == 'timeout':
                    await ctx.send(':alarm_clock: **Time\'s up bud**')
                else:
                    if not ctx.voice_state.voice:
                        await ctx.invoke(self._join)
                    try:
                        song = Song(source)
                        await ctx.voice_state.songs.put(song)
                        if ctx.voice_state.is_playing:
                            await ctx.send('Queued {}'.format(str(source)),delete_after=5)
                        else:
                            await ctx.send('Playing {}'.format(str(source)),delete_after=5)
                    except: 
                        await ctx.send('There was an error downloading ' + song,delete_after=5)    
                    


    @commands.command(aliases=['e'], brief='Turns showing embeds for songs playing off')
    async def embed(self, ctx):
        #await ctx.message.delete()


        # Inverse boolean value to loop and unloop.
        ctx.voice_state.sendEmbed = not ctx.voice_state.sendEmbed
        await ctx.send('Showing now playing embeds after new songs is now ' + ('on' if ctx.voice_state.sendEmbed else 'off'),delete_after=5)

    @commands.command(aliases=['st'], brief='Skips to a song in queue')
    async def skipto(self, ctx, number: int=0):
        if number == 0:
            return await ctx.send('Input a number to skip to in queue')
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!')
        
        for n in range(number-1):
            ctx.voice_state.songs.remove(0)
            n+=1
        ctx.voice_state.skip()
        await ctx.send(f'{ctx.author.mention} has skipped **{number}** song(s)'), 
    
    @commands.command(aliases=['cq'], brief='Clears the queue')
    async def clearqueue(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send('I am not currently in a voice channel!')
        await ctx.send('Are you sure you want clear the queue? Reply **y** for yes and **n** for no')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content.lower() == 'y':
            pass
        elif msg.content.lower() == 'n':
            return await ctx.send('Continuing')
        else:
            return await ctx.send('Please reply with **y** or **n** next time, continuing')
        ctx.voice_state.songs.clear()
        emb=discord.Embed(title='Cleared the queue',color=discord.Colour.blue())
        return await ctx.send(embed=emb,delete_after=5)

    '''                
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,reaction:discord.Reaction):
        await asyncio.sleep(1)
        server = self.bot.get_guild(self.svid)
        global counter
        while True:
            if server.voice_client and server.voice_client.is_playing():
                if not self.vc is None:
                    await asyncio.sleep(5)
                    if counter == 20:
                        await self.vc.msg.edit(embed=self.vc.current.now_embed())
                        counter = 0
                    else:
                        counter += 1
                        await asyncio.sleep(1)
'''
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction,user):
        global loop_value
        message: discord.Message = reaction.message
        msg = message.channel
        serverid = msg.guild.id
        server = self.bot.get_guild(serverid)
        self.svid = serverid


        if reaction.emoji == '⏮️':
            if user.id == self.bot.user.id:
                return
            vc = server.voice_client
            await message.remove_reaction(reaction.emoji,user)
            await msg.send('Currently not working!')
            return

        if reaction.emoji == '▶️':
            if user.id == self.bot.user.id:
                return
            now = datetime.datetime.now() 
            current_time = now.strftime("%H:%M|%m/%d/%Y")
            print(f"{server.name}/{message.channel}/  {current_time}  /{user.name}>  RESUME_BUTTON  ")
            if server.voice_client.is_paused():
                if not  server.voice_client.is_playing():
                    server.voice_client.resume()
                    await message.remove_reaction(reaction.emoji,user)
                    embed = discord.Embed(title=f'{user.name} has resumed the song!',color=discord.Colour.blue())
                    await msg.send(embed=embed,delete_after=5)
                else:
                    await msg.send('The song is currently resumed!',delete_after=5)
                    await message.remove_reaction(reaction.emoji,user)

            else:
                await msg.send('The bot is currently playing, first pause the song with the emoji',delete_after=5)
                await message.remove_reaction(reaction.emoji,user)

        if reaction.emoji == '⏸️':
            if user.id == self.bot.user.id:
                return
            now = datetime.datetime.now() 
            current_time = now.strftime("%H:%M|%m/%d/%Y")
            print(f"{server.name}/{message.channel}/  {current_time}  /{user.name}>  PAUSE_BUTTON  ")
            if server.voice_client.is_playing():
                if not server.voice_client.is_paused():
                    server.voice_client.pause()
                    await message.remove_reaction(reaction.emoji,user)
                    embed = discord.Embed(title=f'{user.name} has paused the song!',color=discord.Colour.blue())
                    await msg.send(embed=embed,delete_after=5)
                else:
                    await msg.send('The song is currently paused!',delete_after=5)
                    await message.remove_reaction(reaction.emoji,user)
            else:
                await msg.send('I am not currently playing anything!',delete_after=5)
                await message.remove_reaction(reaction.emoji,user)

        if reaction.emoji == '🔁':
            if user.id == self.bot.user.id:
                return
            now = datetime.datetime.now() 
            current_time = now.strftime("%H:%M|%m/%d/%Y")
            print(f"{server.name}/{message.channel}/  {current_time}  /{user.name}>  LOOP_BUTTON  ")
            vc = server.voice_client
            if not vc and vc.is_playing():
                await msg.send('I am not currently playing anything',delete_after=5)
                await message.remove_reaction(reaction.emoji,user)
            else:    
                if server.voice_client.is_playing():
                    await message.remove_reaction(reaction.emoji,user)
                    self.vc.loop = not self.vc.loop
                    embed = discord.Embed(title='Song loop is now turned ' + ('**on**' if self.vc.loop else '**off**'),color=discord.Colour.blue())
                    if self.vc.loop is False:
                        loop_value = 0
                    elif self.vc.loop is True:
                        loop_value = 1 
                    await message.edit(embed=self.vc.current.now_embed())
                    await msg.send(embed=embed,delete_after=5)

        if reaction.emoji == '🔀':
            if user.id == self.bot.user.id:
                return
            now = datetime.datetime.now() 
            current_time = now.strftime("%H:%M|%m/%d/%Y")
            print(f"{server.name}/{message.channel}/  {current_time}  /{user.name}>  SHUFFLE_BUTTON  ")
            vc = server.voice_client
            if not vc.is_playing():
                await message.remove_reaction(reaction.emoji,user)
                return await msg.send('I am not currently playing anything!',delete_after=5)
            if len(self.vc.songs) == 0:
                emb=discord.Embed(title='Empty Queue',color=discord.Colour.blue())
                await message.remove_reaction(reaction.emoji,user)
                return await msg.send(embed=emb,delete_after=5)
            self.vc.songs.shuffle()
            embed = discord.Embed(title=f'{user.name} has shuffled the queue',color=discord.Colour.blue())
            await message.remove_reaction(reaction.emoji,user)
            await msg.send(embed=embed,delete_after=5)
        
        if reaction.emoji == '⏭️':
            if user.id == self.bot.user.id:
                return
            now = datetime.datetime.now() 
            current_time = now.strftime("%H:%M|%m/%d/%Y")
            print(f"{server.name}/{message.channel}/  {current_time}  /{user.name}>  SKIP_BUTTON  ")
            if not server.voice_client or not server.voice_client.is_connected():
                return await msg.send('I am not currently in a voice channel!')
            if len(self.vc.songs) == 0: 
                if self.vc.autoplay:
                    self.vc.skip()
                    sembed = discord.Embed(title=f'{user.name} has skipped the song!',color=discord.Colour.blue())
                    await message.remove_reaction(reaction.emoji,user)
                    return await msg.send(embed=sembed,delete_after=5)
                elif self.vc.loop:
                    self.vc.skip()
                    sembed = discord.Embed(title=f'{user.name} has skipped the song!',color=discord.Colour.blue())
                    await message.remove_reaction(reaction.emoji,user)
                    return await msg.send(embed=sembed,delete_after=5)
                else: #not ctx.voice_state.loop and not ctx.voice_state.autoplay:
                    await message.remove_reaction(reaction.emoji,user)
                    return await msg.send('Empty queue, autoplay and loop not on, cannot skip the song',delete_after=5)
            else:
                self.vc.skip()
                await message.remove_reaction(reaction.emoji,user)
                sembed = discord.Embed(title=f'{user.name} has skipped the song!',color=discord.Colour.blue())
                await msg.send(embed=sembed,delete_after=5)

        if reaction.emoji == '➕':
            if user.id == self.bot.user.id:
                return
            now = datetime.datetime.now() 
            current_time = now.strftime("%H:%M|%m/%d/%Y")
            print(f"{server.name}/{message.channel}/  {current_time}  /{user.name}>  PLUS_BUTTON  ")
            vc = server.voice_client
            if not vc or not vc.is_connected():
                await msg.send('I am not currently in a voice channel',delete_after=5)
                return
            if not vc and vc.is_playing():
                return await msg.send('I am not currently playing anything!',delete_after=5)
            else:
                if self.vc.current.source.volume >= 1.50:
                    self.vc.current.source.volume == 1.50
                    await message.remove_reaction(reaction.emoji,user)
                    embed = discord.Embed(title='Max volume limit 150%!',color=discord.Colour.blue())
                    await msg.send(embed=embed,delete_after=5)
                else:
                    if self.vc.loop is True:
                        if self.vc._volume >= 1.50:
                            self.vc._volume == 1.50
                            await message.remove_reaction(reaction.emoji,user)
                            embed = discord.Embed(title='Max volume limit 150%!',color=discord.Colour.blue())
                            await msg.send(embed=embed,delete_after=5)
                        self.vc._volume += 0.25
                        print(self.vc._volume)
                    else:
                        server.voice_client.source.volume += 0.25
                        print(server.voice_client.source.volume)
                    await message.edit(embed=self.vc.current.now_embed())
                    await message.remove_reaction(reaction.emoji,user)
        if reaction.emoji == '➖':
            if user.id == self.bot.user.id:
                return
            now = datetime.datetime.now() 
            current_time = now.strftime("%H:%M|%m/%d/%Y")
            print(f"{server.name}/{message.channel}/  {current_time}  /{user.name}>  MINUS_BUTTON  ")
            vc = server.voice_client
            if not vc or not vc.is_connected():
                await msg.send('I am not currently in a voice channel',delete_after=5)
                return
            if not vc and vc.is_playing():
                return await msg.send('I am not currently playing anything!',delete_after=5)
            else:
                if self.vc.current.source.volume <= 0.25:
                    self.vc.current.source.volume == 0.25
                    await message.remove_reaction(reaction.emoji,user)
                    embed = discord.Embed(title='Min volume limit 25%!',color=discord.Colour.blue())
                    await msg.send(embed=embed,delete_after=5)
                else: 
                    if self.vc.loop is True:
                        if self.vc._volume >= 0.25:
                            self.vc._volume == 0.25
                            await message.remove_reaction(reaction.emoji,user)
                            embed = discord.Embed(title='Min volume limit 25%!',color=discord.Colour.blue())
                            await msg.send(embed=embed,delete_after=5)
                        self.vc._volume -= 0.25
                        print(self.vc._volume)
                    else:
                        server.voice_client.source.volume -= 0.25
                        print(server.voice_client.source.volume)
                    await message.edit(embed=self.vc.current.now_embed())
                    await message.remove_reaction(reaction.emoji,user)

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send('You are not connected to any voice channel')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.send('Bot is already in a voice channel')


    


def setup(bot):
    bot.add_cog(Music(bot))
    print('--------------------------')
    print('music cog betöltve!')
    print('--------------------------')