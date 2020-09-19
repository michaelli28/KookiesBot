import asyncio
import functools
import itertools
import math
import random
import re
import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands
import httpx
from bs4 import BeautifulSoup
import asyncio

import discord
import youtube_dl
from discord.ext import commands









youtube_dl.utils.bug_reports_message = lambda: ''

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

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
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
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
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
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

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
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))
        
        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @classmethod
    async def search_source(cls, bot: commands.Bot, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        channel = ctx.channel
        loop = loop or asyncio.get_event_loop()

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

        lst.append('\n**Type a number to make a choice, Type `cancel` to exit**')
        cls.search["description"] = "\n".join(lst)

        em = discord.Embed.from_dict(cls.search)
        await ctx.send(embed=em, delete_after=45.0)

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
                duration.append('{}'.format(hours))
            if minutes > 0:
                duration.append('{}'.format(minutes))
            if seconds > 0:
                duration.append('{}'.format(seconds))
            
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

    def create_embed(self):
        embed = (discord.Embed(title='Now playing', description='```css\n{0.source.title}\n```'.format(self), color=random.randint(0, 0xffffff))
                .add_field(name='Duration', value=self.source.duration)
                .add_field(name='Requested by', value=self.requester.mention)
                .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                .set_thumbnail(url=self.source.thumbnail)
                .set_author(name=self.requester.name, icon_url=self.requester.avatar_url))
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
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.song_history = []
        self.exists = True

        self._loop = False
        self._autoplay = True
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

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
                if self.autoplay and self.current:
                    try:
                        async with timeout(15):
                            self.current = await self.songs.get()
                    except asyncio.TimeoutError:
                        # Spoof user agent to show whole page.
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'}
                        song_url = self.current.source.url
                        # Get the page
                        async with httpx.AsyncClient() as client:
                            response = await client.get(song_url, headers=headers)

                        soup = BeautifulSoup(response.text, features='lxml')

                        # Parse all the recommended videos out of the response and store them in a list
                        recommended_urls = []
                        for li in soup.find_all('li', class_='related-list-item'):
                            a = li.find('a')

                            # Only videos (no mixes or playlists)
                            if 'content-link' in a.attrs['class']:
                                recommended_urls.append(
                                    f'https://www.youtube.com{a.get("href")}')

                        ctx = self._ctx

                        # Chose the next song so that it wasnt played recently

                        next_song = recommended_urls[0]

                        for recommended_url in recommended_urls:
                            not_in_history = True
                            for song in self.song_history[:15]:
                                if recommended_url == song.source.url:
                                    not_in_history = False
                                    break

                            if not_in_history:
                                next_song = recommended_url
                                break

                        async with ctx.typing():
                            try:
                                source = await YTDLSource.create_source(ctx, next_song, loop=self.bot.loop)
                            except YTDLError as e:
                                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                                self.bot.loop.create_task(self.stop())
                                self.exists = False
                                return
                            else:
                                song = Song(source)
                                self.current = song
                                await ctx.send('Autoplaying {}'.format(str(source)))

                else:
                    try:
                        async with timeout(180):  # 3 minutes
                            self.current = await self.songs.get()
                    except asyncio.TimeoutError:
                        self.bot.loop.create_task(self.stop())
                        self.exists = False
                        return

                self.song_history.insert(0, self.current)
                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)
                await self.current.source.channel.send(embed=self.current.create_embed())

            #If the song is looped
            elif self.loop == True:
                self.song_history.insert(0, self.current)
                self.now = discord.FFmpegPCMAudio(
                    self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS)
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

        if self.voice:
            await self.voice.disconnect()
            self.voice = None
















class MusicPlayer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
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

    #async def cog_command_error(self, ctx , error: commands.CommandError):
    #    await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != self.bot.user.id:
            print(f"{message.guild}/{message.channel}/{message.author.name}>{message.content}")
            if message.embeds:
                print(message.embeds[0].to_dict())

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Joins a voice channel."""
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send('Specify a channel or join one')

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.send(f'Connected to: **{destination}**')
    @commands.command(name='summon')
    async def _summon(self, ctx , *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.
        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            raise VoiceError(
                'You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.send(f'Connected to: **{destination}**')
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect'])
    async def _leave(self, ctx ):
        """Clears the queue and leaves the voice channel."""
        channel = ctx.author.voice.channel
        if not ctx.voice_state.voice:
            return await ctx.send('Not connected to any voice channel.')

        await ctx.voice_state.stop()
        await ctx.send('Left **' + channel+'**')
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume', aliases=['vol','v'])
    async def _volume(self, ctx , *, volume: int):
        """Sets the volume of the player."""
        if volume > 70 and ctx.author.id != 'NotThatBot#3360':
            return await ctx.send("Volume exceeds 70 percent, safety implemented to reduce hearing loss, ask NotThatBot#3360 for manual override")

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        if 0 > volume > 100:
            return await ctx.send('Volume must be between 0 and 70')

        ctx.voice_state.volume = volume / 100
        await ctx.send('Volume of the player set to **{}**%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing', 'np'])
    async def _now(self, ctx ):
        """Displays the currently playing song."""
        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause')
    async def _pause(self, ctx ): 
        """Pauses the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!')
        elif ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()

            await ctx.send(f'{ctx.author.mention} has paused the song!')


    @commands.command(name='resume', aliases=['re', 'res','r'])
    async def _resume(self, ctx ):
        """Resumes a currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything')
        elif ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            vc.resume()
            await ctx.send(f'{ctx.author.mention} has resumed the song!')


    @commands.command(name='stop')
    async def _stop(self, ctx):
        await ctx.send('Are you sure you want to stop the song and delete queues and settings? Replay y for yes and n for no')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content.lower()=='y':
            await ctx.send('Stopping player and clearing queue')
        elif msg.content.lower()=='n':
            return await ctx.send('Continuing')
        else:
            return await ctx.send('Please reply with y or n next time, continuing')
        """Stops playing song and clears the queue."""
        ctx.voice_state.songs.clear()
        if ctx.voice_state.autoplay:
            ctx.voice_state.autoplay = False
            await ctx.send('Autoplay is now turned off')
        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()


    @commands.command(name='skip')
    async def _skip(self, ctx ):        
        if not ctx.voice_state.is_playing:
            return await ctx.send('I am not currently playing anything')

        ctx.voice_state.skip()
        await ctx.send(f'{ctx.author.mention} has skipped the song!')

    @commands.command(name='queue', aliases=['check','q'])
    async def _queue(self, ctx , *, page: int = 1):
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!')
        
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page
        if page > pages:
            return await ctx.send('The page can\'t be larger than the number of pages')
        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(
                i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)


    @commands.command(name='shuffle')
    async def _shuffle(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!')
        """Shuffles the queue."""
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Queue is empty')
        ctx.voice_state.songs.shuffle()
        await ctx.send(f'{ctx.author.mention} has shuffled the queue')


    @commands.command(name='remove')
    async def _remove(self, ctx , index: int):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Queue is empty')
        else:
            ctx.voice_state.songs.remove(index - 1)
            await ctx.send('Removed song number **'+ index + '**')

    @commands.command(name='loop')
    async def _loop(self, ctx ):
        """Loops the currently playing song.
        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.send('Song loop is now turned ' + ('on' if ctx.voice_state.loop else 'off'))

    @commands.command(name='autoplay')
    async def _autoplay(self, ctx):
        """Automatically queue a new song that is related to the song at the end of the queue.
        Invoke this command again to toggle autoplay the song.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!')

        elif not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.autoplay = not ctx.voice_state.autoplay
        await ctx.message.add_reaction('✅')
        await ctx.send('Autoplay after end of queue is now ' + ('on' if ctx.voice_state.autoplay else 'off') )
    
    @commands.command(name='play')
    async def _play(self, ctx, *, search: str):
        """Plays a song.
        If there are songs in the queue, this will be queued until the
        other songs finished playing.
        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
            else:
                if not ctx.voice_state.voice:
                    await ctx.invoke(self._join)
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                if ctx.voice_state.is_playing:
                    await ctx.send('Queued {}'.format(str(source)))
                else:
                    await ctx.send('Playing {}'.format(str(source)))


    @commands.command(aliases=['pl'])
    async def playlist(self, ctx, *, url):
        maxPlaylistSize = 50
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
                    source = await YTDLSource.create_source(ctx, 'https://www.youtube.com/watch?v='+ playlist_urls[n], loop=self.bot.loop)
                    song = Song(source)

                    await ctx.voice_state.songs.put(song)
                
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                self.bot.loop.create_task(SongQueue().clear())
                self.exists = False
                return
    @commands.command(name='history')
    async def _history(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's history.
        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.song_history) == 0:
            return await ctx.send('Empty history.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.song_history) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.song_history[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='{} tracks:\n\n{}'.format(len(ctx.voice_state.song_history), queue))
                .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)
    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError(
                'You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError(
                    'Bot is already in a voice channel.')


bot = commands.Bot(command_prefix=';')


@bot.command(name='botstop', aliases=['bstop'])
@commands.is_owner()
async def botstop(ctx):
    print('Goodbye')
    await ctx.send('Goodbye')
    await bot.logout()
    return

@bot.event
async def on_ready():
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))


def setup(bot):
    bot.add_cog(MusicPlayer(bot))
