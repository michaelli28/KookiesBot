import asyncio
import functools
import itertools
import math
import random
import re
import requests
import discord
from collections import OrderedDict
import datetime
import youtube_dl
from async_timeout import timeout
from discord.ext import commands
import httpx
from bs4 import BeautifulSoup
import asyncio
import discord
from discord.utils import get
from discord.ext import commands
import math
from typing import Optional
#import pyprog
from time import sleep

youtube_dl.utils.bug_reports_message = lambda: ''


timestamp = 0
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': f'-vn -ss {timestamp}'
    }
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

    # FFMPEG_OPTIONS = {
    #     'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    #     'options': '-vn',
    # }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)
    ytdl.cache.remove()

    def __init__(self, ctx, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.1):
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
        
        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **FFMPEG_OPTIONS), data=info)

    @classmethod
    async def search_source(cls, bot: commands.Bot, ctx, search: str, *, loop: asyncio.BaseEventLoop = None, timestamp: int=0):
        channel = ctx.channel
        loop = loop or asyncio.get_event_loop()

        cls.search_query = '%s%s:%s' % ('ytsearch', 10, ''.join(search))

        partial = functools.partial(cls.ytdl.extract_info, cls.search_query, download=False, process=False)
        info = await loop.run_in_executor(None, partial)

        cls.search = {}
        cls.search["title"] = f'Search results for:\n**{search}**'
        cls.search["type"] = 'rich'
        cls.search["color"] = 7506394
        cls.search["author"] = {'name': f'{ctx.author.display_name}', 'url': f'{ctx.author.avatar_url}', 'icon_url': f'{ctx.author.avatar_url}'}
        
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
                    rtrn = cls(ctx, discord.FFmpegPCMAudio(data['url'], **FFMPEG_OPTIONS), data=data)
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

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester
    
    def getsourceurl(self):
        return self.source.url

    def create_embed(self):
        embed = (discord.Embed(title='Now playing', description='```css\n{0.source.title}\n```'.format(self), color=random.randint(0, 0xffffff))
                .add_field(name='Duration', value=self.source.duration)
                .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Volume', value=f'**{self.source.volume*100}**%')
                .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self), inline=False)
                .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                .set_thumbnail(url=self.source.thumbnail)
                .set_author(name=self.requester.display_name, icon_url=self.requester.avatar_url))
        embed.timestamp = datetime.datetime.now()
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
        self._volume = 0.1
        self.skip_votes = set()

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
                    async with timeout(10):
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    # embed = discord.Embed(color=random.randint(0, 0xffffff))
                    # embed.add_field(name='Timed Out... couldn\'t get next song within 15 seconds', value='Leaving the voice channel')
                    # embed.timestamp = datetime.datetime.now()
                    self.bot.loop.create_task(self.stop())
                    self.exists = False
                    return #await ctx.send(embed=embed)
                    #     # Spoof user agent to show whole page.
                    #     headers = {
                    #         'User-Agent': 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'}
                    #     song_url = self.current.source.url
                    #     # Get the page
                    #     async with httpx.AsyncClient() as client:
                    #         response = await client.get(song_url, headers=headers)

                    #     soup = BeautifulSoup(response.text, features='lxml')

                    #     # Parse all the recommended videos out of the response and store them in a list
                    #     recommended_urls = []
                    #     for li in soup.find_all('li', class_='related-list-item'):
                    #         a = li.find('a')

                    #         # Only videos (no mixes or playlists)
                    #         if 'content-link' in a.attrs['class']:
                    #             recommended_urls.append(
                    #                 f'https://www.youtube.com{a.get("href")}')

                    #     ctx = self._ctx

                    #     # Chose the next song so that it wasnt played recently

                    #     next_song = recommended_urls[0]

                    #     for recommended_url in recommended_urls:
                    #         not_in_history = True
                    #         for song in self.song_history[:15]:
                    #             if recommended_url == song.source.url:
                    #                 not_in_history = False
                    #                 break

                    #         if not_in_history:
                    #             next_song = recommended_url
                    #             break

                    #     async with ctx.typing():
                    #         try:
                    #             source = await YTDLSource.create_source(ctx, next_song, loop=self.bot.loop)
                    #         except YTDLError as e:
                    #             await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                    #             self.bot.loop.create_task(self.stop())
                    #             self.exists = False
                    #             return
                    #         else:
                    #             song = Song(source)
                    #             self.current = song
                    #             await ctx.send('Autoplaying {}'.format(str(source)))

                # else:
                #     try:
                #         async with timeout(180):  # 3 minutes
                #             self.current = await self.songs.get()
                #     except asyncio.TimeoutError:
                #         self.bot.loop.create_task(self.stop())
                #         self.exists = False
                #         return
                self.song_history.insert(0, self.current)
                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)
                # async def stopplayer():
                #     await self.voice.disconnect()
                #     self.voice = None
                # if self.songs.qsize()>0:
                #     self.voice.play(self.current.source, after=self.play_next_song)
                # else:
                #     self.voice.play(self.current.source, after=await stopplayer())
                if self.sendEmbed:
                    msg: discord.Message= await self.current.source.channel.send(embed=self.current.create_embed())
                    
                    #await msg.add_reaction('⏪')
                    await msg.add_reaction('⏯️')
                    await msg.add_reaction('⏩')
                    await msg.add_reaction('🔁')
                    await msg.add_reaction('🔀')
                    await msg.add_reaction('⏹️')
                    await msg.add_reaction('🔈')
                    await msg.add_reaction('🔊')

            #If the song is looped
            elif self.loop == True:
                self.song_history.insert(0, self.current)
                self.now = discord.FFmpegPCMAudio(
                    self.current.source.stream_url, **FFMPEG_OPTIONS)
                self.current.source.volume = self._volume

                # if ctx.voice_client:
                #     ctx.voice_client.source.volume = self._volume/100
                # ctx.voice_state.current.source.volume = self._volume/100
                # ctx.voice_state.volume = self._volume/100
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











class music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        self.vc = None
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
        self.ctx = ctx
    #async def cog_command_error(self, ctx , error: commands.CommandError):
    #    await ctx.send('An error occurred: {}'.format(str(error)))


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        
        msg = reaction.message
        if msg.author.id != self.bot.user.id:
            return
        channel = msg.channel

        

        if reaction.emoji=='⏯️':
            ctx = self.ctx
            await msg.remove_reaction(reaction, user)
            vc = self.vc
            if not ctx.voice_client:
                return await channel.send(f'{user.mention}, I am not currently playing anything')
            elif vc.voice.is_playing():
                vc.voice.pause()
                await channel.send(f'{user.mention} has paused the song!')

            elif vc.voice.is_paused():
                ctx.voice_client.resume()
                await channel.send(f'{user.mention} has resumed the song!')
        if reaction.emoji=='⏩':
            ctx = self.ctx
            await msg.remove_reaction(reaction, user)
            vc = self.vc
            if not ctx.voice_client or not ctx.voice_client.is_connected:
                return await channel.send(f'{user.mention}, I am not currently in a voice channel!')
            if len(vc.songs) == 0: 
                if vc.autoplay:
                    vc.skip()
                    return await channel.send(f'{user.mention} has skipped the song!')
                elif vc.loop:
                    vc.skip()
                    return await channel.send(f'{user.mention} has skipped the song!')
                else: #not ctx.voice_state.loop and not ctx.voice_state.autoplay: 
                    return await channel.send(f'{user.mention}, empty queue, autoplay and loop not on, cannot skip the song')
            else:
                vc.skip()
                await channel.send(f'{user.mention} has skipped the song!')
        if reaction.emoji=='🔀':
            ctx = self.ctx
            await msg.remove_reaction(reaction, user)
            vc = self.vc
            if len(vc.songs) == 0:
                return await channel.send(f'{user.mention}, queue is empty')
            else:
                vc.songs.shuffle()
                await channel.send(f'{user.mention} has shuffled the queue')
        if reaction.emoji == '🔁':
            ctx = self.ctx
            await msg.remove_reaction(reaction, user)
            vc = self.vc
            try:
                if not vc.is_playing:
                    return await channel.send(f'{user.mention}, I am not currently playing anything')
                else:
                    vc.loop = not vc.loop
                    await channel.send(f'{user.mention}, song loop is now turned ' + ('**on**' if vc.loop else '**off**'))

            except:
                pass
            
        if reaction.emoji=='🔈':
            ctx = self.ctx
            await msg.remove_reaction(reaction, user)
            vc = self.vc
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                return await channel.send(f'{user.mention}, I am not currently in a voice channel')
            volume = vc.volume*100
            if volume-10 < 0:
                volume = 0
            else:
                volume = volume-10
            if vc:
                vc.volume = volume/100
            vc.current.source.volume = volume/100
            vc.volume = volume/100
            await channel.send(f'{user.mention} has set the volume to **{volume}**%', delete_after=10)

        if reaction.emoji=='🔊':
            ctx = self.ctx
            await msg.remove_reaction(reaction, user)
            vc = self.vc
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                return await channel.send(f'{user.mention}, I am not currently in a voice channel')
            volume = vc.volume*100
            if volume+10 > 100:
                volume = 100
            else:
                volume = volume+10
            if vc:
                vc.volume = volume/100
            vc.current.source.volume = volume/100
            vc.volume = volume/100
            await channel.send(f'{user.mention} has set the volume to **{volume}**%', delete_after=10)

        if reaction.emoji == '⏹️':
            ctx = self.ctx
            await msg.remove_reaction(reaction, user)
            vc = ctx.voice_client
            if not vc or not vc.is_connected:
                return await channel.send(f'{user.mention}, I am not currently in a voice channel!')
            else:
                await channel.send(f'{user.mention}, stopping player and clearing queue')
                if ctx.voice_state.is_playing:
                    ctx.voice_state.voice.pause()
                await ctx.voice_state.stop()
                del self.voice_states[ctx.guild.id]

            ctx.voice_state.songs.clear()





    @commands.command(name='join', aliases=['j'], brief='Makes the bot join a voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _join(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Joins a voice channel"""
        #await ctx.message.delete()
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send(f'{ctx.author.mention}, specify a channel for me to join or join one')

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.send(f'{ctx.author.mention}, connected to: **{destination}**, type **;leave** to leave the channel')
            return
        ctx.voice_state.voice = await destination.connect()
        return await ctx.send(f'{ctx.author.mention}, connected to: **{destination}**, type **;leave** to leave the channel')


    @commands.command(name='summon', brief='Summons the bot to a channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _summon(self, ctx , *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel
        If no channel was specified, it joins your channel
        """
        #await ctx.message.delete()
        if not channel and not ctx.author.voice:
            return ctx.send(f'{ctx.author.mention}, you are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.send(f'{ctx.author.mention}, connected to: **{destination}** type **;leave** to leave the channel')
            return

        ctx.voice_state.voice = await destination.connect()
        return
    @commands.command(name='leave', aliases=['disconnect', 'l'], brief='Makes the bot leave the channel it is in')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _leave(self, ctx):
        """Clears the queue and leaves the voice channel"""
        #await ctx.message.delete()
        try:
            channel = ctx.author.voice.channel
        except:
            return await ctx.send(f'{ctx.author.mention}, join the voice channel that Kookies is in!')
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')

        await ctx.voice_state.stop()
        ctx.voice_state.exists = False
        await ctx.send('Left **' + str(channel) + '**')
        del self.voice_states[ctx.guild.id]
        return 
        
    @commands.command(name='volume', aliases=['vol','v'], brief='Set the volume of the music')
    async def _volume(self, ctx, *, volume: int = None):
        """Sets the volume of the player"""

        if volume == None:
            try:
                return await ctx.send(f'{ctx.author.mention}, current volume is at **{ctx.voice_client.source.volume*100}**%')
            except:
                return await ctx.send(f'{ctx.author.mention}, current volume is at **{ctx.voice_state.volume*100}**%')
        # if volume > 80:
        #     return await ctx.send("Volume exceeds 80 percent, safety implemented to reduce hearing loss, ask NotThatBot#3360 for manual override")

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel')

        if 0 > volume or volume > 100:
            return await ctx.send(f'{ctx.author.mention}, vvolume must be between 0 and 100')
        
        if ctx.voice_state.loop is True:
            ctx.voice_state._volume = volume/100
            ctx.voice_state.current.source.volume = volume/100
            ctx.voice_state.volume = volume/100
        else:
            if ctx.voice_client:
                ctx.voice_client.source.volume = volume/100
            ctx.voice_state.current.source.volume = volume/100
            ctx.voice_state.volume = volume/100

        # if ctx.voice_state.loop == True:
        #     ctx.voice_state._volume = volume/100
        #     ctx.voice_state.current.source.volume = volume/100
        #     ctx.voice_state.volume = volume/100
        #     print(ctx.voice_state.volume)
        #     print(ctx.voice_state._volume)
        #     print(ctx.voice_state.current.source.volume)
        # else:
        #     if ctx.voice_client:
        #         ctx.voice_client.source.volume = volume/100

        #     ctx.voice_state.current.source.volume = volume/100
        #     ctx.voice_state.volume = volume/100
        #     print(ctx.voice_state.volume)
        #     print(ctx.voice_state._volume)
        #     print(ctx.voice_state.current.source.volume)
        return await ctx.send(f'{ctx.author.mention} has set the volume to **{volume}**%')


    # @commands.command(brief='Override for volume, NotThatBot#3360 only')
    # @commands.is_owner()
    # async def voln(self, ctx, *, volume: int=None):

    #     if volume == None:
    #         return await ctx.send(f'Current volume is at **{ctx.voice_client.source.volume}%**')
    #     """Sets the volume of the player"""
    #     vc = ctx.voice_client

    #     if not vc or not vc.is_connected():
    #         return await ctx.send('I am not currently playing anything')
    #     if 0 > volume > 100:
    #         return await ctx.send('Volume must be between 0 and 100')
    #     if ctx.voice_client:
    #         ctx.voice_client.source.volume = volume/100
    #     ctx.voice_state.volume = volume/100
    #     await ctx.send('Volume of the player set to **{}**%'.format(volume))


    @commands.command(name='now', aliases=['current', 'playing', 'np'], brief='Shows the song that is playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _now(self, ctx):
        #await ctx.message.delete()
        vc = ctx.voice_client
        if not vc:
            return await ctx.send('I am not currently playing anything')
        return await ctx.send(embed=ctx.voice_state.current.create_embed())

        
    @commands.command(name='pause', aliases=['pau'], brief='Pauses the song playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _pause(self, ctx): 
        """Pauses the currently playing song"""
        #await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send(f'{ctx.author.mention}, I am not currently playing anything!')
        elif ctx.voice_state.is_playing:
            ctx.voice_state.voice.pause()

            return await ctx.send(f'{ctx.author.mention} has paused the song!')


    @commands.command(name='resume', aliases=['re', 'res','r'], brief='Resumes the song')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _resume(self, ctx ):
        """Resumes a currently paused song"""
        #await ctx.message.delete()
        vc = ctx.voice_client
        if not vc.is_playing:
            return await ctx.send(f'{ctx.author.mention}, I am not currently playing anything!')
        if not vc.is_paused:
            return await ctx.send(f'{ctx.author.mention}, song is not paused')

        elif ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            vc.resume()
            return await ctx.send(f'{ctx.author.mention} has resumed the song!')


    @commands.command(name='stop', brief='Stops the music, clears the queue, and disconnects the bot from the voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _stop(self, ctx):

        await ctx.send('Are you sure you want to stop the song and delete queues and settings? Reply **y** for yes and **n** for no')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content.lower()=='y':
            await ctx.send(f'{ctx.author.mention}, stopping player and clearing queue')
        elif msg.content.lower()=='n':
            return await ctx.send(f'{ctx.author.mention}, continuing')
        else:
            return await ctx.send(f'{ctx.author.mention}, please reply with **y** or **n** next time, continuing')

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.pause()
        await ctx.voice_state.stop()
        ctx.voice_state.exists = False
        del self.voice_states[ctx.guild.id]


        return ctx.voice_state.songs.clear()

        # if ctx.voice_state.autoplay:
        #     ctx.voice_state.autoplay = False
        #     await ctx.send('Autoplay is now turned off')


    @commands.command(name='skip', brief='Skips the song playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _skip(self, ctx):
        #await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')
        if len(ctx.voice_state.songs) == 0: 
            if ctx.voice_state.autoplay:
                ctx.voice_state.skip()
                return await ctx.send(f'{ctx.author.mention} has skipped the song!')
            elif ctx.voice_state.loop:
                ctx.voice_state.skip()
                return await ctx.send(f'{ctx.author.mention} has skipped the song!')
            else: #not ctx.voice_state.loop and not ctx.voice_state.autoplay: 
                return await ctx.send(f'{ctx.author.mention}, Empty queue, autoplay and loop not on, cannot skip the song')
        else:
            ctx.voice_state.skip()
            return await ctx.send(f'{ctx.author.mention} has skipped the song!')

    @commands.command(name='queue', aliases=['check','q'], brief='Checks the queue for songs')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _queue(self, ctx , *, page: int = 1):
        """Shows the player's queue
        You can optionally specify the page to show. Each page contains 10 elements.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected:
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')
        
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send(f'{ctx.author.mention}, empty queue')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page
        if page > pages:
            return await ctx.send(f'{ctx.author.mention}, the page can\'t be larger than the number of pages')
        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '{0}. [{1.source.title}]({1.source.url})\n'.format(
                i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        embed.timestamp = datetime.datetime.now()
        return await ctx.send(embed=embed)


    @commands.command(name='shuffle', brief='Shuffles the queue')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _shuffle(self, ctx):
        #await ctx.message.delete()
        vc = ctx.voice_client
        if not vc.is_playing:
            return await ctx.send(f'{ctx.author.mention}, I am not currently playing anything!')
        """Shuffles the queue"""
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send(f'{ctx.author.mention}, queue is empty')
        ctx.voice_state.songs.shuffle()
        return await ctx.send(f'{ctx.author.mention} has shuffled the queue')


    @commands.command(name='remove', brief='Removes a song from a queue')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _remove(self, ctx , index: int):
        """Removes a song from the queue at a given index"""
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send(f'{ctx.author.mention}, queue is empty')
        elif index > len(ctx.voice_state.songs):
            return await ctx.send(f'{ctx.author.mention}, invalid index, number too large')
        else:
            ctx.voice_state.songs.remove(index - 1)
            return await ctx.send(f'{ctx.author.mention}, removed song number **'+ str(index) + '**')

    @commands.command(name='loop', brief='Loops the song currently playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _loop(self, ctx):
        """Loops the currently playing song
        Invoke this command again to unloop the song
        """
        #await ctx.message.delete()
        if not ctx.voice_state.is_playing:
            return await ctx.send(f'{ctx.author.mention}, I am not currently playing anything')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.send(f'{ctx.author.mention}, song loop is now turned ' + ('**on**' if ctx.voice_state.loop else '**off**'))

    # @commands.command(name='autoplay', aliases=['a'])
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def _autoplay(self, ctx):
    #     """Automatically queue a new song that is related to the song at the end of the queue.
    #     Invoke this command again to toggle autoplay the song.
    #     """
    #     #await ctx.message.delete()
    #     vc = ctx.voice_client

    #     if not vc or not vc.is_connected():
    #         return await ctx.send('I am not currently connected to voice!')

    #     # Inverse boolean value to loop and unloop.
    #     ctx.voice_state.autoplay = not ctx.voice_state.autoplay
    #     await ctx.send('Autoplay after end of queue is now ' + ('**on**' if ctx.voice_state.autoplay else '**off**'))
    
    @commands.command(name='play', brief='Plays or queues a song or playlist by link or by search')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _play(self, ctx, *, search: str=None):
        """Plays a song
        If there are songs in the queue, this will be queued until the
        other songs finished playing
        This command automatically searches from various sites if no URL is provided
        """
        
        voiceconnect = get(ctx.bot.voice_clients, guild=ctx.guild)

        if search == None:
            return await ctx.send(f'{ctx.author.mention}, you need to input a url or search')

        httpS = re.findall('www.',search)
        pList = re.findall('list=',search)
        indexL = re.findall('index=',search)
        watch = re.findall('watch',search)

        async with ctx.typing():
            if len(httpS)>0 and len(pList)>0:
                if len(indexL)==0 and len(watch)==0:

                    maxPlaylistSize = 40
                    showVidSize = None
                    # Spoof user agent to show whole page.

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'}
                    # Get the page

                    async with httpx.AsyncClient() as client:
                        response = await client.get(search, headers=headers)
                    playlist_urls = re.findall('watch\?v=(.*?)\\\\u0026list=', response.text)

                    if len(playlist_urls) >= maxPlaylistSize:
                        showVidSize = maxPlaylistSize
                    else:
                        showVidSize = len(playlist_urls)

                    # try:
                    if not voiceconnect or not voiceconnect.is_connected():
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
                    # except youtube_dl.utils.ExtractorError as e:
                    #     await ctx.send(f'{ctx.author.mention}, an error occurred while processing this request: {e} Note: if this is 429, then I can\'t do anything about it as YouTube does this automatically')
                elif len(watch)>0:
                    response = requests.get(search)
                    soup = BeautifulSoup(response.text, 'lxml')
                    playlistUrls = re.findall('"url":"/watch\?v=(.*?)"' , soup.prettify())
                    playlistUrls2 = []

                    for url in playlistUrls:
                        url2 = re.findall('(.*?)\\\\u0026list=', url)

                        if len(url2)>0:
                            playlistUrls2.append(url2[0])
                        else:
                            playlistUrls2.append(url)

                    # for i in range(len(playlistUrls2)):
                    #     if len(playlistUrls2[i][0]) > 3:
                    #         playlistUrls2.append(playlistUrls2[i][0])
                    #         playlistUrls2.remove(playlistUrls2[i])
                    # print(playlistUrls2)

                    res = [i for n, i in enumerate(playlistUrls2) if i not in playlistUrls2[:n]]
                    maxPlaylistSize = 40
                    showVidSize = None

                    if len(res) >= maxPlaylistSize:
                        showVidSize = maxPlaylistSize
                    else:
                        showVidSize = len(res)
                    # try:
                    if not voiceconnect or not voiceconnect.is_connected():
                        await ctx.invoke(self._join)

                    await ctx.send(f'{ctx.author.mention}, putting songs into the queue, please wait a minute or two before checking the queue')
                    for n in range(showVidSize):
                        # try:
                        source = await YTDLSource.create_source(ctx, 'https://www.youtube.com/watch?v=' + res[n], loop=self.bot.loop)
                        song = Song(source)
                        await ctx.voice_state.songs.put(song)
                        # except youtube_dl.utils.ExtractorError:
                        #     return await ctx.send(f'{ctx.author.mention}, an error occurred while processing this request: {e} Note: if this is 429, then I can\'t do anything about it as YouTube does this automatically')
                        # except:
                        #     await ctx.send(f'{ctx.author.mention}, there was an error downloading ' + 'https://www.youtube.com/watch?v=' + res[n])
                    return
                    # except YTDLError as e:
                    #     await ctx.send(f'{ctx.author.mention}, an error occurred while processing this request: {e} Note: if this is 429, then I can\'t do anything about it as YouTube does this automatically')

            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)

            except youtube_dl.utils.ExtractorError as e:
                return await ctx.send(f'{ctx.author.mention}, an error occurred while processing this request: {e} Note: if this is 429, then I can\'t do anything about it as YouTube does this automatically')
            else:
                if not voiceconnect or not voiceconnect.is_connected():
                    await ctx.invoke(self._join)

                song = Song(source)
                await ctx.voice_state.songs.put(song)

                if ctx.voice_state.is_playing:
                    return await ctx.send('Queued {}'.format(str(source)))
                else:
                    return await ctx.send('Playing {}'.format(str(source)))

    @commands.command(name='seek', brief='Plays or queues a song or playlist by link or by search')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def seek(self, ctx, timestamp=0):
        async with ctx.typing():
            timestamp = timestamp
            source = await YTDLSource.create_source(ctx, ctx.voice_state.current.source.url, loop=self.bot.loop)
            song = Song(source)
            await ctx.voice_state.songs.put(song)
            return await ctx.send(f'{ctx.author.mention}, seeking to {timestamp} seconds')
    '''@commands.command() 
    async def playlist(self, ctx, *, url):
        maxPlaylistSize = 40
        showVidSize = None
        # Spoof user agent to show whole page.
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'}
        # Get the page
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        playlist_urls = re.findall('watch\?v=(.*?)\\\\u0026list=', response.text)
        if len(playlist_urls) >= maxPlaylistSize:
            showVidSize = maxPlaylistSize
        else:
            showVidSize = len(playlist_urls)
            
        async with ctx.typing():
            try:
                if not ctx.voice_state.voice:
                    await ctx.invoke(self._join)
                await ctx.send('Putting songs into the queue, please wait a minute or two before checking the queue')
                for n in range(showVidSize):
                    source = await  YTDLSource.create_source(ctx, 'https://www.youtube.com/watch?v='+ playlist_urls[n], loop=self.bot.loop)
                    song = Song(source)

                    await ctx.voice_state.songs.put(song)
                
            except  YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))'''

    @commands.command(name='history', aliases=['h','his'], brief='Shows the history of songs played')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _history(self, ctx, *, page: int = 1):
        """Shows the player's history.
        You can optionally specify the page to show. Each page contains 10 elements.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(f'{ctx.author.mention}, I am not currently connected to voice!')
        
        if len(ctx.voice_state.song_history) == 0:
            return await ctx.send(f'{ctx.author.mention}, empty history')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.song_history) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.song_history[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='{} tracks:\n\n{}'.format(len(ctx.voice_state.song_history), queue))
                .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        embed.timestamp = datetime.datetime.now()
        return await ctx.send(embed=embed)
    
    @commands.command(name='search', brief='Shows 10 search results for videos')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _search(self, ctx, *, search: str=None):
        """Searches youtube.
        It returns an imbed of the first 10 results collected from youtube.
        Then the user can choose one of the titles by typing a number
        in chat or they can cancel by typing "cancel" in chat.
        Each title in the list can be clicked as a link.
        """

        if (search)==None:
            return await ctx.send(f'{ctx.author.mention}, input a search')
        async with ctx.typing():
            try:
                source = await YTDLSource.search_source(self.bot, ctx, search, loop=self.bot.loop)
            except youtube_dl.utils.ExtractorError as e:
                await ctx.send(f'{ctx.author.mention}, an error occurred while processing this request: {e} Note: if this is 429, then I can\'t do anything about it as YouTube does this automatically')
            else:
                if source == 'sel_invalid':
                    await ctx.send('Invalid selection')
                elif source == 'cancel':
                    await ctx.send(':white_check_mark:')
                elif source == 'timeout':
                    await ctx.send(':alarm_clock: **Time\'s up bud**')
                else:
                    if not ctx.voice_state.voice:
                        try:
                            await ctx.invoke(self._join)
                        except:
                            pass
                    try:
                        song = Song(source)
                        await ctx.voice_state.songs.put(song)
                        if ctx.voice_state.is_playing:
                            return await ctx.send('Queued {}'.format(str(source)))
                        else:
                            return await ctx.send('Playing {}'.format(str(source)))
                    except: 
                        return await ctx.send(f'{ctx.author.mention}, there was an error downloading ' + song)    
                    


    @commands.command(aliases=['e'], brief='Turns showing embeds for songs playing off')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def embed(self, ctx):
        #await ctx.message.delete()


        # Inverse boolean value to loop and unloop.
        ctx.voice_state.sendEmbed = not ctx.voice_state.sendEmbed
        return await ctx.send(f'{ctx.author.mention}, showing now playing embeds after new songs is now ' + ('on' if ctx.voice_state.sendEmbed else 'off'))

    @commands.command(aliases=['st'], brief='Skips to a song in queue')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def skipto(self, ctx, number: int=0):
        if number == 0:
            return await ctx.send(f'{ctx.author.mention}, input a number to skip to in queue')
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(f'{ctx.author.mention}, I am not currently connected to voice')
        
        for n in range(number-1):
            ctx.voice_state.songs.remove(0)
            n+=1
        ctx.voice_state.skip()
        return await ctx.send(f'{ctx.author.mention} has skipped **{number}** song(s)'), 
    
    @commands.command(aliases=['cq'], brief='Clears the queue')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def clearqueue(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')
        await ctx.send(f'{ctx.author.mention}, are you sure you want clear the queue? Reply **y** for yes and **n** for no')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content.lower() == 'y':
            pass
        elif msg.content.lower() == 'n':
            return await ctx.send('Continuing')
        else:
            return await ctx.send(f'{ctx.author.mention}, please reply with **y** or **n** next time, continuing')
        ctx.voice_state.songs.clear()
        return await ctx.send(f'{ctx.author.mention}, cleared the queue')



    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(f'{ctx.author.mention}, you are not connected to any voice channel')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.send(f'{ctx.author.mention}, bot is already in a voice channel')





def setup(bot):
    bot.add_cog(music(bot))
