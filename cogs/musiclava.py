import math
import lavalink
import ksoftapi
import discord
import random
from discord.ext import commands
import datetime
import asyncio
kclient = ksoftapi.Client('eyJ0IjogImFwcCIsICJrIjogImtobWFjc2lnIiwgInBrIjogbnVsbCwgIm8iOiAiNTg3MDY4NjEwMjM3NjkzOTYzIiwgImMiOiA3NTczNDQ4fQ.bdb3a6d6f99d566327126abc55fdbd969b04c877ccd7cd5c5df316a343e80355')
class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kclient = kclient

        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(bot.user.id)
            # Host, Port, Password, Region, Name
            # Host, Port, Password, Region, Name
            bot.lavalink.add_node(
                'kookieslavalink.herokuapp.com', 80, 'youshallnotpass', 'us', 'default-node')
            bot.add_listener(bot.lavalink.voice_update_handler,
                            'on_socket_response')

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.lavalink._event_hooks.clear()

    # async def cog_command_error(self, ctx, error):
    #     if isinstance(error, commands.CommandInvokeError):
    #         return await ctx.send(error.original)

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.ctx.send('Queue ended, leaving channel')
            return await self.connect_to(guild_id, None)
        # if isinstance(event, lavalink.events.TrackStartEvent):
        #     return await self.now(self.ctx)
            
    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None
        self.ctx = ctx

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region))
        should_connect = ctx.command.name in ('play',)

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('Join a voice channel first :loud_sound:')

        if not player.is_connected:
            if not should_connect:
                return await ctx.send('Not connected :mute:')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                return await ctx.send('I need the `CONNECT` and `SPEAK` permissions :disappointed_relieved:')

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                return await ctx.send('You need to be in my voice channel :loud_sound:')

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        ws = self.bot._connection._get_websocket(guild_id)
        return await ws.voice_state(str(guild_id), channel_id)

    @commands.command(name='play', brief='Plays or queues a song or playlist by link or by search')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx, *, query: str=None):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        query = query.strip('<>')

        if not query.startswith('http'):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Song not found :x: please try again :mag_right:')

        em = discord.Embed(color = random.randint(0,0xffffff))
        em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar_url)
        em.timestamp = datetime.datetime.utcnow()

        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)

            em.title = 'Playlist Enqueued!'
            em.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            print(track)
            em.title = 'Track Enqueued'
            em.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            em.set_thumbnail(
                url=f"http://i.ytimg.com/vi/{track['info']['identifier']}/hqdefault.jpg")

            em.add_field(name='Channel', value=track['info']['author'])
            if track['info']['isStream']:
                duration = 'Live'
            else:
                duration = lavalink.format_time(
                    track['info']['length']).lstrip('00:')
            em.add_field(name='Duration', value=duration)

            track = lavalink.models.AudioTrack(
                track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        msg = await ctx.send(embed=em)

        if not player.is_playing:
            await player.play()
            await player.reset_equalizer()
            await msg.delete(delay=1)
            # await self.now(ctx)
            return await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))

    @commands.command(name='search', brief='Searches for a song a returns the top 10 results')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def search(self, ctx, *, query):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = f'ytsearch:{query}'
        results = await player.node.get_tracks(query)
        tracks = results['tracks'][0:10]
        i = 0
        query_result = ''
        embed = discord.Embed()
        embed.description = query_result
        embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        for track in tracks:
            i = i + 1
            query_result = query_result + f'{i}) {track["info"]["title"]}\n{track["info"]["uri"]}\n'

        
        await ctx.channel.send(embed=embed)

        em = discord.Embed(color=random.randint(0, 0xffffff))
        def check(m):
            return m.author.id == ctx.author.id
        
        response = await self.bot.wait_for('message', check=check)
        track = tracks[int(response.content)-1]

        player.add(requester=ctx.author.id, track=track)
        em.title = 'Track Enqueued'
        em.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
        em.set_thumbnail(
            url=f"http://i.ytimg.com/vi/{track['info']['identifier']}/hqdefault.jpg")

        em.add_field(name='Channel', value=track['info']['author'])
        if track['info']['isStream']:
            duration = 'Live'
        else:
            duration = lavalink.format_time(
                track['info']['length']).lstrip('00:')

        em.add_field(name='Duration', value=duration)
        em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
        msg = await ctx.send(embed=em)
        if not player.is_playing:
            await player.play()
            await player.reset_equalizer()
            await msg.delete(delay=1)
            # await self.now(ctx)
            return await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))

    @commands.command(name='seek', brief='Seeks to a point in the song (positive seconds moves the song forward that much while negative seconds moves the song backward that much')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def seek(self, ctx, seconds: int=None):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')

        if not seconds:
            return await ctx.send('You need to specify the amount of seconds to seek :fast_forward:')
        try:
            track_time = player.position + int(seconds) * 1000
            await player.seek(track_time)
        except ValueError:
            return await ctx.send('Specify valid amount of seconds :clock3:')

        return await ctx.send(f'Moved track to **{lavalink.format_time(track_time)}**')

    @commands.command(name='skip', brief='Skips the song playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')

        await ctx.send('⏭ Skipped')
        return await player.skip()

    @commands.command(name='skipto', brief='Skips to a song in the queue')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _skipto(self, ctx, index: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')
        track = player.queue[index-1]
        for i in range(index-1):
            await player.skip()
        return await ctx.send(f"⏭ Skipped to {track['info']['title']}")
        
    @commands.command(name='now', aliases=['current', 'playing', 'np'], brief='Shows the song that is playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def now(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        song = 'Nothing'

        if player.current:
            if player.current.stream:
                dur = 'LIVE'
                pos = ''
                count = total = 1
            else:
                count = player.position
                pos = lavalink.format_time(count)
                total = player.current.duration
                dur = lavalink.format_time(total)
                if pos == dur:  # When called immediatly after enqueue
                    count = 0
                    pos = '00:00:00'
                dur = dur.lstrip('00:')
                pos = pos[-len(dur):]
            bar_len = 30  # bar length
            filled_len = int(bar_len * count // float(total))
            bar = '═' * filled_len + '◈' + '─' * (bar_len - filled_len)
            song = f'[{player.current.title}]({player.current.uri})\n`{pos} {bar} {dur}`'

            em = discord.Embed(color=random.randint(0,0xffffff), description=song)
            em.add_field(name='Channel', value=f'{player.current.author}')
            if player.repeat:
                em.add_field(name='Loop', value=f'On')
            else:
                em.add_field(name='Loop', value=f'Off')
            em.set_author(name="Now Playing 🎵",
                          icon_url="https://i.ibb.co/DGsmTvh/star.gif")
            em.set_thumbnail(
                url=f"http://i.ytimg.com/vi/{player.current.identifier}/hqdefault.jpg")
            requester = ctx.guild.get_member(player.current.requester)
            em.set_footer(
                text=f"Requested by: {requester}", icon_url=requester.avatar_url)
            em.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=em)
            return await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))
        else:
            return await ctx.send('Not playing anything :mute:')

    @commands.command(name='save', aliases=['star'], brief='Saves the song playing to your dm')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def savetodm(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.current:
            if player.current.stream:
                dur = 'Live'
            else:
                dur = lavalink.format_time(
                    player.current.duration).lstrip('00:')
            song = f'[{player.current.title}]({player.current.uri})'
            em = discord.Embed(colour=discord.Colour(
                0x59FFC8), description=song)
            em.set_author(name="Now Playing 🎵",
                          icon_url="https://i.ibb.co/DGsmTvh/star.gif")
            em.set_thumbnail(
                url=f"http://i.ytimg.com/vi/{player.current.identifier}/hqdefault.jpg")
            em.add_field(name='Channel', value=player.current.author)
            em.add_field(name='Duration', value=dur)
            em.timestamp = datetime.datetime.utcnow()
            user = ctx.author
            await user.send(embed=em)
            await ctx.send(f"Current song has been sent to you {ctx.author.mention} :floppy_disk:")
        else:
            await ctx.send('Not playing anything :mute:')

    @commands.command(name='queue', aliases=['q'], brief='Checks the queue for songs')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def queue(self, ctx, page: int = 1):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('Queue empty! :cd:')

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ''

        for i, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{i + 1}.` [{track.title}]({track.uri})\n'

        embed = discord.Embed(color=random.randint(0,0xffffff),
                              description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)

    @commands.command(name='resume', aliases=['r'], brief='Resumes the song')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def resume(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')

        if player.paused:
            await player.set_pause(False)
            return await ctx.send('Resumed ▶')
        else:
            return await ctx.send('Already playing')

    @commands.command(name='pause', aliases=['pau'], brief='Pauses the song playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pause(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything')

        if player.paused:
            return await ctx.send('Not playing, cannot pause')
        else:
            await player.set_pause(True)
            return await ctx.send('Paused ⏸')

    @commands.command(name='volume', aliases=['vol', 'v'], brief='Set the volume of the music')
    async def volume(self, ctx, volume: int = None):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not volume:
            return await ctx.send(f'🔈 The volume is at {player.volume}%')
        if volume > 100 and str(ctx.author.id) != '587068610237693963':
            return await ctx.send('Saving eardrums, ask owner for override over 100 percent volume')
        await player.set_volume(volume)
        return await ctx.send(f'🔈 Set to {player.volume}%')

    @commands.command(name='shuffle', brief='Shuffles the queue')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shuffle(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')

        player.shuffle = not player.shuffle

        return await ctx.send('🔀 Shuffle ' + ('enabled' if player.shuffle else 'disabled'))

    @commands.command(name='loop', brief='Loops/repeats the current song playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def loop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')

        player.repeat = not player.repeat

        return await ctx.send('Loop ' + ('enabled' if player.repeat else 'disabled'))

    @commands.command(name='remove', brief='Removes a song from a queue')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove(self, ctx, index: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('Nothing queued :cd:')

        if index > len(player.queue) or index < 1:
            return await ctx.send('Index has to be greater than 0 and less than or equal to the queue size')

        index = index - 1
        removed = player.queue.pop(index)

        return await ctx.send('Removed **' + removed.title + '** from the queue.')

    @commands.command(name='leave', aliases=['stop'], brief='Makes the bot leave the channel it is in')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def disconnect(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('You\'re not in my voice channel :loud_sound:')

        if not player.is_connected:
            return await ctx.send('Not connected :mute:')

        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await ctx.send('Stopping :mute:')
        return await self.connect_to(ctx.guild.id, None)
        


    @commands.command(name='lyrics', aliases=['ly'], brief='Get the lyrics of a song')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def get_lyrics(self, ctx, *, query: str = ""):
        if not query:
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)

            if not player.is_playing:
                return await ctx.send('I\'m not currently playing anything :warning:')
            query = player.current.title

        try:
            async with ctx.typing():
                results = await self.kclient.music.lyrics(query, limit=1)
        except ksoftapi.NoResults:
            await ctx.send(f'No lyrics found for `{query}`')
        else:
            lyrics = results[0].lyrics
            result = results[0]
            embed = discord.Embed(title=f'{result.name} - {result.artist}',
                                  color=random.randint(0,0xffffff), description=lyrics[:2048])
            embed.set_thumbnail(url=result.album_art)
            embed.set_author(name="Lyrics:")
            embed.timestamp = datetime.datetime.utcnow()
            lyrics = lyrics[2048:]
            embeds = [embed]  # create embeds' list for long lyrics
            while len(lyrics) > 0 and len(embeds) < 10:  # limiting embeds to 10
                embed = discord.Embed(color=random.randint(0,0xffffff), description=lyrics[:2048])
                lyrics = lyrics[len(embeds)*2048:]
                embed.timestamp = datetime.datetime.utcnow()
                embeds.append(embed)
            # set footer for last embed
            embeds[-1].set_footer(text="Source: KSoft.Si")
            for embed in embeds:
                await ctx.send(embed=embed)
            
            return

    @commands.command(name='equalizer', aliases=['eq'], brief='Change frequencies')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def equalizer(self, ctx, *args):
        """Equalizer"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if len(args) == 0:
            await ctx.send('Specify `band gain` or `preset` to change frequencies :control_knobs:')
        elif len(args) == 1:
            presets = {
                'reset': 'Default',
                'bassboost': [0.08, 0.12, 0.2, 0.18, 0.15, 0.1, 0.05, 0.0, 0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14],
                'jazz': [-0.13, -0.11, -0.1, -0.1, 0.14, 0.2, -0.18, 0.0, 0.24, 0.22, 0.2, 0.0, 0.0, 0.0, 0.0],
                'pop': [-0.02, -0.01, 0.08, 0.1, 0.15, 0.1, 0.03, -0.02, -0.035, -0.05, -0.05, -0.05, -0.05, -0.05, -0.05],
                'treble': [-0.1, -0.12, -0.12, -0.12, -0.08, -0.04, 0.0, 0.3, 0.34, 0.4, 0.35, 0.3, 0.3, 0.3, 0.3]
            }

            preset = args[0].lower()
            if preset in ['reset', 'default']:
                await player.reset_equalizer()
            elif preset in presets:
                gain_list = enumerate(presets[preset])
                await player.set_gains(*gain_list)

            elif preset == '--list':
                em = discord.Embed(title=':control_knobs: EQ presets:', color=random.randint(0,0xffffff), description='\n'.join(presets.keys()))
                em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar_url)
                em.timestamp = datetime.datetime.utcnow()
                return await ctx.send(embed=em)
            else:
                return await ctx.send('Invalid preset specified \nType `~eq --list` for all presets')
        elif len(args) == 2:
            try:
                band = int(args[0])
                gain = float(args[1])
                await player.set_gain(band, gain)
            except ValueError:
                return await ctx.send('Specify valid `band gain` values :control_knobs:')
        else:
            return await ctx.send('Specify `band gain` or `preset` :control_knobs:')
        # Print final EQ settings
        eq_frequencies = [f"`{gain}`" for gain in player.equalizer]
        return await ctx.send("Current Values:\n" + ' '.join(eq_frequencies))


def setup(bot):
    bot.add_cog(music(bot))
