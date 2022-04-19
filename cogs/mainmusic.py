import math
import lavalink
import ksoftapi
import discord
import random
from discord.ext import commands
from discord import Embed
import datetime
import asyncio
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from typing import Optional
import asyncio
import sys
import traceback
import json
import json

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
# URL conversions.
import urllib.request
import bs4
import youtube
import re
from pymongo import MongoClient
kclient = ksoftapi.Client('1931343e09f8c6434c51af90c3a602ac06c29211')
url_rx = re.compile(r'https?://(?:www\.)?.+')
#TODO skipto cmd
#TODO lavalink errors
#TODO make sure when errors happen, things dont keep going on
#TODO make volume guild based
#TODO make song loop cmd
#TODO make move song to cmd
#TODO make soundcloud search using scsearch:blahblahblah

with open('config.json', 'r') as config:
        configfile = json.load(config)
        config.close()
cooldown = int(configfile['cooldown'])
times = int(configfile['numberoftimes'])

class menu(MenuPages):
    def reaction_check(self, payload):

        if payload.message_id != self.message.id:
            return False
        if payload.user_id in {self.bot.user.id}:
            return False

        return payload.emoji in self.buttons


class HelpMenu(ListPageSource):
    def __init__(self, ctx, bot, data):
        self.ctx = ctx
        self.place = 1
        self.bot = bot
        super().__init__(data, per_page=10)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)
        player = self.bot.lavalink.player_manager.get(self.ctx.guild.id)
        embed = Embed(
            title=f"Music Queue For {self.ctx.guild.name}", color=random.randint(0, 0xffffff), description=f'**Now playing - [{player.current.title}]({player.current.uri})**')
        # embed.set_thumbnail(url=self.ctx.me.avatar.url)
        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} songs")
        embed.timestamp = datetime.datetime.utcnow()
        try:
            embed.set_author(name=self.ctx.author.display_name,
                icon_url=self.ctx.author.avatar.url)
        except:
            embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
        

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        n = (menu.current_page)*10+1
        for entry in entries:
            fields.append((f'{n})', f'[{entry.title}]({entry.uri})'))

            n+=1
        self.place += 1

        return await self.write_page(menu, fields)

def getTracks(playlistURL):
    # Creating and authenticating our Spotify app.
    # client_credentials_manager = SpotifyClientCredentials(APIs["spotify"]["client_id"], APIs["spotify"]["client_secret"])
    client_credentials_manager = SpotifyClientCredentials('2c0c71f3b5dc43a2a26e6862135b7b68','2419402a673e4774b323f9160aca088d')
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Getting a playlist.
    results = spotify.user_playlist_tracks(user="",playlist_id=playlistURL)
    # print(results)

    # print (yaml.dump(results['items'], default_flow_style=False))
    # print (json.dumps(results, indent=8))
    trackList = []
    # For each track in the playlist.
    for i in results["items"]:
        # In case there's only one artist.
        if (i["track"]["artists"].__len__() == 1):
            # We add trackName - artist.
            trackList.append(i["track"]["name"] + " - " + i["track"]["artists"][0]["name"])
        # In case there's more than one artist.
        else:
            nameString = ""
            # For each artist in the track.
            for index, b in enumerate(i["track"]["artists"]):
                nameString += (b["name"])
                # If it isn't the last artist.
                if (i["track"]["artists"].__len__() - 1 != index):
                    nameString += ", "
            # Adding the track to the list.
            trackList.append(i["track"]["name"] + " - " + nameString)
        # trackList.append(i['track']['name'])
    # print(trackList)
    return trackList

class Playlist(ListPageSource):
    def __init__(self, ctx, data, saver, playlistname):
        self.ctx = ctx
        self.place = 1
        self.saver = saver
        self.playlistname = playlistname
        super().__init__(data, per_page=10)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(
            title=f"Playlist `{self.playlistname}` for {self.saver}", color=random.randint(0, 0xffffff))
        # embed.set_thumbnail(url=self.ctx.guild.me.avatar.url)

        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} songs")

        embed.timestamp = datetime.datetime.utcnow()
        try:
            embed.set_author(name=self.ctx.author.display_name,
                icon_url=self.ctx.author.avatar.url)
        except:
            embed.set_author(name=self.ctx.author.display_name,
                icon_url=self.ctx.author.default_avatar.url)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        n = (menu.current_page)*10+1
        for entry in entries:
            fields.append((f'{n})', f"[{entry['info']['title']}]({entry['info']['uri']})"))

            n+=1
        self.place += 1

        return await self.write_page(menu, fields)

class LavalinkVoiceClient(discord.VoiceClient):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        # ensure there exists a client already
        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node('lavalink.islantay.tk', 8880, 'waifufufufu', 'us', 'default-node')
            # self.client.lavalink.add_node('kookiesllnew.herokuapp.com', 80, 'youshallnotpass', 'us', 'default-node')


            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
                't': 'VOICE_SERVER_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
                't': 'VOICE_STATE_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def disconnect(self, *, force: bool) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that
        # would set channel_id to None doesn't get dispatched after the 
        # disconnect
        player.channel_id = None
        self.cleanup()

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kclient = kclient
        self.volume = 40


        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(bot.user.id)


            # bot.lavalink.add_node('localhost', 80, 'youshallnotpass', 'us', 'default-node')

            # bot.lavalink.add_node('kookiesll1.herokuapp.com', 80, 'youshallnotpass', 'us', 'default-node')
            
            # bot.lavalink.add_node('kookiesll2.herokuapp.com', 80, 'youshallnotpass', 'us', 'default-node')
            
            # bot.lavalink.add_node('kookiesll3.herokuapp.com', 80, 'youshallnotpass', 'us', 'default-node')
            # bot.lavalink.add_node('kookiesllnew.herokuapp.com', 80, 'youshallnotpass', 'us', 'default-node') #on first acct
            bot.lavalink.add_node('lavalink.islantay.tk', 8880, 'waifufufufu', 'us', 'default-node')
            bot.add_listener(bot.lavalink.voice_update_handler,
                            'on_socket_response')

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.lavalink._event_hooks.clear()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            return await ctx.send(error.original)

        error = getattr(error, 'original', error)
        if isinstance(error, commands.CommandNotFound):
            if ctx.message.content.startswith(';)'):
                return
            await ctx.send(f'`{ctx.message.content}` is not a valid command')

        elif isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace(
                'guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format(
                    "**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'I need the **{}** permission(s) to run this command.'.format(
                fmt)
            await ctx.send(_message)
            return

        elif isinstance(error, discord.errors.Forbidden):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send('I don\'t have permissions to do that')
        elif isinstance(error, commands.CommandOnCooldown):
            try:
                await ctx.message.delete()
            except:
                pass
            await ctx.send('{}, That command is on cooldown! Try again in {:.2f}s!'.format(ctx.author.mention, error.retry_after))

        elif isinstance(error, commands.NotOwner):
            try:
                await ctx.message.delete()
            except:
                pass
            return await ctx.send('{}, That command is for the owner of the bot only (NotThatBot#3360)'.format(ctx.author.mention))
            
        elif isinstance(error, commands.MissingPermissions):
            ctx.command.reset_cooldown(ctx)
            missing = [perm.replace('_', ' ').replace(
                'guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format(
                    "**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'You need the **{}** permission(s) to use this command.'.format(
                fmt)
            return await ctx.send(_message)

        elif isinstance(error, commands.UserInputError):
            ctx.command.reset_cooldown(ctx) 
            await ctx.send("Invalid input")

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except discord.Forbidden:
                pass
            return
            
        print('Ignoring exception in command {}:'.format(
            ctx.command), file=sys.stderr)

        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            await channel.send('Queue ended, leaving channel')
            return await guild.voice_client.disconnect(force=True)
            # player = event.player
            # channel = self.bot.get_channel(player.fetch(guild_id))
            # player.delete(guild_id)
            # activity = discord.Game(name=";help")
            # await self.bot.change_presence(activity=activity)
             
            # return await self.connect_to(guild_id, None)
        if isinstance(event, lavalink.events.TrackStartEvent):
            guild_id = int(event.player.guild_id)
            player = event.player
            channel = self.bot.get_channel(player.fetch(guild_id))

            guild = self.bot.get_guild(guild_id)
            
            me = guild.me
            await me.edit(deafen=True)
            try:
                members = guild.me.voice.channel.members
                if len(members)==1:
                    await self.ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
                    # await self.connect_to(guild_id, None)
                    return await channel.send('The voice channel that the bot is in has no members, leaving voice channel')
            except Exception as e:
                print(e)

            song = 'Nothing'
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
            em.add_field(name='Author', value=f'{player.current.author}')
            if player.repeat:
                em.add_field(name='Queue Loop', value=f'On')
            else:
                em.add_field(name='Queue Loop', value=f'Off')
            if player.shuffle:
                em.add_field(name='Shuffle', value='On')
            else:
                em.add_field(name='Shuffle', value='Off')
            em.add_field(name='Volume', value=f'{player.volume}%')
            em.set_author(name="Now Playing 🎵",
                        icon_url="https://i.ibb.co/DGsmTvh/star.gif")
            em.set_thumbnail(
                url=f"http://i.ytimg.com/vi/{player.current.identifier}/hqdefault.jpg")
            requester = guild.get_member(player.current.requester)
            try:
                em.set_footer(
                text=f"Requested by: {requester}", icon_url=requester.avatar.url)
            except:
                em.set_footer(
                text=f"Requested by: {requester}", icon_url=requester.default_avatar.url)
            
            em.timestamp = datetime.datetime.utcnow()
            await channel.send(embed=em)

            # await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))
            return 

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
            ctx.guild.id, endpoint='us-central')
        
        should_connect = ctx.command.name in ('play', 'search','scsearch', 'scplay','playlist', 'ptest')
        
        # if not ctx.author.voice or not ctx.author.voice.channel:
        #     raise commands.CommandInvokeError('Join a voice channel first :loud_stop'sound:')
        not_connect = ctx.command.name in ('volume', 'disconnect', 'stop', 'join', 'pause', 'resume')
        if ctx.command.name in ['lyrics', 'searchlyrics']:
            return
        if not player.is_connected:
            if not should_connect and not not_connect:
                raise commands.CommandInvokeError('Not connected :mute:')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions. :disappointed_relieved:')


            player.store('channel', ctx.channel.id)
            try:
                await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
            except:
                raise commands.CommandInvokeError('Try joining a voice channel, by the looks of it, you aren\'t in one')
        else:
            pass
            # if int(player.channel_id) != ctx.author.voice.channel.id:
            #     raise commands.CommandInvokeError('You need to be in my voice channel :loud_sound:')

    # async def connect_to(self, guild_id: int, channel_id: str):
    #     """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
    #     ws = self.bot._connection._get_websocket(guild_id)
    #     return await ws.voice_state(str(guild_id), channel_id)

    @commands.command(name='join', brief='Makes the bot join a voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _join(self, ctx: commands.Context, channel: discord.VoiceChannel = None):
        """Joins a voice channel"""
        # await ctx.message.delete()
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send(f'{ctx.author.mention}, specify a channel for me to join or join one')

        destination = ctx.author.voice.channel
        # await self.connect_to(ctx.guild.id, (str(destination.id)))
        await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        return await ctx.send(f'{ctx.author.mention}, connected to: **{destination.name}**, type **;leave** to leave the channel')


    # @commands.command()
    # async def ptest(self, ctx, *, query: str):
    #     """ Searches and plays a song from a given query. """
    #     # Get the player for this guild from cache.
    #     player = self.bot.lavalink.player_manager.get(ctx.guild.id)
    #     # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
    #     query = query.strip('<>')

    #     # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
    #     # SoundCloud searching is possible by prefixing "scsearch:" instead.
    #     if not url_rx.match(query):
    #         query = f'ytsearch:{query}'

    #     # Get the results for the query from Lavalink.
    #     results = await player.node.get_tracks(query)

    #     # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
    #     # ALternatively, resullts['tracks'] could be an empty array if the query yielded no tracks.
    #     if not results or not results['tracks']:
    #         return await ctx.send('Nothing found!')

    #     embed = discord.Embed(color=discord.Color.blurple())

    #     # Valid loadTypes are:
    #     #   TRACK_LOADED    - single video/direct URL)
    #     #   PLAYLIST_LOADED - direct URL to playlist)
    #     #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
    #     #   NO_MATCHES      - query yielded no results
    #     #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
    #     if results['loadType'] == 'PLAYLIST_LOADED':
    #         tracks = results['tracks']

    #         for track in tracks:
    #             # Add all of the tracks from the playlist to the queue.
    #             player.add(requester=ctx.author.id, track=track)

    #         embed.title = 'Playlist Enqueued!'
    #         embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
    #     else:
    #         track = results['tracks'][0]
    #         embed.title = 'Track Enqueued'
    #         embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

    #         # You can attach additional information to audiotracks through kwargs, however this involves
    #         # constructing the AudioTrack class yourself.
    #         track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
    #         player.add(requester=ctx.author.id, track=track)

    #     await ctx.send(embed=embed)

    #     # We don't want to call .play() if the player is playing as that will effectively skip
    #     # the current track.
    #     if not player.is_playing:
    #         await player.play()
    @commands.command(name='play', aliases=['p', 'yt', 'youtube'], brief='Plays or queues a song or playlist by link or by search (youtube), to insert song at an index, search using # as a separator, songnamehere#3 will search for songnamehere and will insert at the 3rd position in the queue')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def play(self, ctx, *, query: str=None):
        if query == None:
            return await ctx.send('You need to input a search')
        
        try:
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)
            query.strip()
            if int(query.find('#')) != -1:
                query = query.split('#',1)
                try:
                    index = int(query[1])
                except ValueError:
                    index = None
                query = query[0]
            else:
                index = None

            async with ctx.typing():
                if index != None:
                    if int(index) > len(player.queue):
                        return await ctx.send('Index is larger than queue size')

                query = query.strip('<>')
                if query.find('http') != -1 and query.find('spotify') != -1:
                    tracks = getTracks(query)
                    # print("URL LIST: ")
                    for i in tracks:
                        # print(i)
                        query = f'ytsearch:{i}'
                        results = await player.node.get_tracks(query)
                        if not results or not results['tracks']:
                            q = i.split(' - ')
                            qu = q[1]
                            qu += ' - '
                            qu += q[0]
                            query = f'ytsearch:{qu}'
                            results = await player.node.get_tracks(query)
                            if not results or not results['tracks']:
                                await ctx.send(f'The song {i} in your playlist was not found, try adding the song manually')
                            else:
                                player.add(requester=ctx.author.id, track=results['tracks'][0])
                        else:
                            player.add(requester=ctx.author.id, track=results['tracks'][0])
                    
                    em = discord.Embed(color = random.randint(0,0xffffff))
                    try:
                        em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                    except:
                        em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
                    em.timestamp = datetime.datetime.utcnow()
                    em.title = 'Playlist Enqueued!'
                    em.description = f'Spotify Playlist - {len(tracks)} tracks'
                    msg = await ctx.send(embed=em)
                    await player.set_volume(self.volume)

                    if player.fetch(ctx.message.guild.id) != None:
                        player.delete(ctx.message.guild.id)
                    player.store(ctx.message.guild.id, ctx.message.channel.id)
                    await ctx.send(f'Sending now playing messages in **{ctx.channel.name}**')
                    
                    if not player.is_playing:
                        await player.play()
                        await player.reset_equalizer()
                        await msg.delete(delay=1)
                        # await self.now(ctx)
                        return
                        # return await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))

                # if not query.startswith('http'):
                #     query = f'ytsearch:{query}'
                if not url_rx.match(query):
                    query = f'ytsearch:{query}'

                results = await player.node.get_tracks(query)

                if not results or not results['tracks']:
                    return await ctx.send('Song not found :x: please try again :mag_right:')

                em = discord.Embed(color = random.randint(0,0xffffff))
                try:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                except:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
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
                    em.title = 'Track Enqueued'
                    em.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                    em.set_thumbnail(
                        url=f"http://i.ytimg.com/vi/{track['info']['identifier']}/hqdefault.jpg")
                    em.add_field(name='Author', value=track['info']['author'])
                    
                    if track['info']['isStream']:
                        duration = 'Live'

                    else:
                        duration = lavalink.format_time(
                            track['info']['length']).lstrip('00:')
                    em.add_field(name='Duration', value=duration)

                    # track = lavalink.models.AudioTrack(
                    #     track, ctx.author.id, recommended=True)
                    
                    track = lavalink.models.AudioTrack(track, ctx.author.id)

                    if index != None:
                        player.add(requester=ctx.author.id, track=track, index=(index-1))
                        em.add_field(name='Position in queue', value=index)

                    else:
                        em.add_field(name='Position in queue', value=len(player.queue)+1)
                        player.add(requester=ctx.author.id, track=track)
                        

                msg = await ctx.send(embed=em)
                await player.set_volume(self.volume)

                if player.fetch(ctx.message.guild.id) != None:
                    player.delete(ctx.message.guild.id)
                player.store(ctx.message.guild.id, ctx.message.channel.id)
                await ctx.send(f'Sending now playing messages in **{ctx.channel.name}**')
                
                if not player.is_playing:
                    await player.play()
                    await player.reset_equalizer()
                    await msg.delete(delay=1)
                    # await self.now(ctx)
                    return
                    # return await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))

        except lavalink.exceptions.NodeException:
            await ctx.send('Node not found, contacting owner for support...')
            me = await self.bot.fetch_user(587068610237693963)
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            return


    @commands.command(name='scplay', aliases=['sc', 'soundcloud'],brief='Plays or queues a song FROM SOUNDCLOUD, to insert song at an index, search using # as a separator, songnamehere#3 will search for songnamehere and will insert at the 3rd position in the queue')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def scplay(self, ctx, *, query: str=None):
        if query == None:
            return await ctx.send('You need to input a search')
        try:
            query.strip()

            if int(query.find('#')) != -1:
                query = query.split('#',1)
                try:
                    index = int(query[1])
                except ValueError:
                    index = None
                query = query[0]
            else:
                index = None

            async with ctx.typing():
                player = self.bot.lavalink.player_manager.get(ctx.guild.id)

                if index != None:

                    if int(index) > len(player.queue):
                        return await ctx.send('Index is larger than queue size')

                query = query.strip('<>')

                if not query.startswith('http'):
                    query = f'scsearch:{query}'
                results = await player.node.get_tracks(query)

                if not results or not results['tracks']:
                    return await ctx.send('Song not found :x: please try again :mag_right:')

                em = discord.Embed(color = random.randint(0,0xffffff))
                try:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                except:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
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
                    em.title = 'Track Enqueued'
                    em.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                    em.set_thumbnail(
                        url=f"http://i.ytimg.com/vi/{track['info']['identifier']}/hqdefault.jpg")
                    em.add_field(name='Author', value=track['info']['author'])
                    
                    if track['info']['isStream']:
                        duration = 'Live'

                    else:
                        duration = lavalink.format_time(
                            track['info']['length']).lstrip('00:')
                    em.add_field(name='Duration', value=duration)

                    # track = lavalink.models.AudioTrack(
                    #     track, ctx.author.id, recommended=True)
                    track = lavalink.models.AudioTrack(track, ctx.author.id)

                    if index != None:
                        player.add(requester=ctx.author.id, track=track, index=(index-1))
                        em.add_field(name='Position in queue', value=index)

                    else:
                        em.add_field(name='Position in queue', value=len(player.queue)+1)
                        player.add(requester=ctx.author.id, track=track)
                        

                msg = await ctx.send(embed=em)
                await player.set_volume(self.volume)

                if player.fetch(ctx.message.guild.id) != None:
                    player.delete(ctx.message.guild.id)
                player.store(ctx.message.guild.id, ctx.message.channel.id)
                await ctx.send(f'Sending now playing messages in **{ctx.channel.name}**')

                if not player.is_playing:
                    await player.play()
                    await player.reset_equalizer()
                    await msg.delete(delay=1)
                    # await self.now(ctx)
                    # return await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))
                    return

        except lavalink.exceptions.NodeException:
            await ctx.send('Node not found, contacting owner for support...')
            me = await self.bot.fetch_user(587068610237693963)
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            return


    @commands.command(name='search', aliases=['ytsearch'], brief='Searches for a song (youtube) and returns the top 10 results')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def search(self, ctx, *, query = None):
        if query == None:
            return await ctx.send('You need to input a search')
        try:
            async with ctx.typing():
                player = self.bot.lavalink.player_manager.get(ctx.guild.id)
                query1 = f'ytsearch:{query}'
                results = await player.node.get_tracks(query1)
                tracks = results['tracks'][0:10]
                i = 0
                query_result = ''
                embed = discord.Embed(title=f'Search results for: {query}')
                try:
                    embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                except:
                    embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
                embed.timestamp = datetime.datetime.utcnow()
                for track in tracks:
                    i = i + 1
                    query_result = query_result + f'{i}) [{track["info"]["title"]}]({track["info"]["uri"]})\nChannel: {track["info"]["author"]}\n\n'

                embed.description = query_result
                await ctx.send(embed=embed)

                em = discord.Embed(color=random.randint(0, 0xffffff))
                def check(m):
                    return m.author.id == ctx.author.id
                try:
                    response = await self.bot.wait_for('message', check=check, timeout=30)
                except asyncio.TimeoutError:
                    return await ctx.send('Timed out, please respond with a number between one through ten to select a song or stop to cancel')
                if response.content.lower() == 'cancel' or response.content.lower() == 'stop':
                    return await ctx.send('Stopping')
                elif int(response.content) > 10:
                    return await ctx.send('Please list a number from 1 to 10')
                track = tracks[int(response.content)-1]

                player.add(requester=ctx.author.id, track=track)
                
                em.title = 'Track Enqueued'
                em.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                em.set_thumbnail(
                    url=f"http://i.ytimg.com/vi/{track['info']['identifier']}/hqdefault.jpg")

                em.add_field(name='Author', value=track['info']['author'])
                if track['info']['isStream']:
                    duration = 'Live'
                else:
                    duration = lavalink.format_time(
                        track['info']['length']).lstrip('00:')

                em.add_field(name='Duration', value=duration)
                try:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                except:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
                em.timestamp = datetime.datetime.utcnow()
                msg = await ctx.send(embed=em)
                await player.set_volume(self.volume)
                if not player.is_playing:
                    await player.play()
                    await player.reset_equalizer()
                    await msg.delete(delay=1)
                    # await self.now(ctx)
                    # return await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))
                    return

        except lavalink.exceptions.NodeException:
            await ctx.send('Node not found, contacting owner for support...')
            me = await self.bot.fetch_user(587068610237693963)
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            return


    @commands.command(name='scsearch', aliases=['soundcloudsearch'], brief='Searches for a song ON SOUNDCLOUD and returns the top 10 results')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def scsearch(self, ctx, *, query = None):
        if query == None:
            return await ctx.send('You need to input a search')
        try:
            async with ctx.typing():
                player = self.bot.lavalink.player_manager.get(ctx.guild.id)
                query = f'scsearch:{query}'
                results = await player.node.get_tracks(query)
                tracks = results['tracks'][0:10]
                i = 0
                query_result = ''
                embed = discord.Embed()
                try:
                    embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                except:
                    embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
                embed.timestamp = datetime.datetime.utcnow()
                for track in tracks:
                    i = i + 1
                    query_result = query_result + f'{i}) {track["info"]["title"]}\n{track["info"]["uri"]}\n\n'

                embed.description = query_result
                await ctx.send(embed=embed)

                em = discord.Embed(color=random.randint(0, 0xffffff))
                def check(m):
                    return m.author.id == ctx.author.id
                try:
                    response = await self.bot.wait_for('message', check=check, timeout=30)
                except asyncio.TimeoutError:
                    return await ctx.send('Please respond with a number between one through ten to select a song or stop to cancel')
                if response.content.lower() == 'cancel' or response.content.lower() == 'stop':
                    return await ctx.send('Stopping')
                elif int(response.content) > 10 or int(response.content) < 1:
                    return await ctx.send('Please list a number from 1 to 10')
                track = tracks[int(response.content)-1]

                player.add(requester=ctx.author.id, track=track)
                
                em.title = 'Track Enqueued'
                em.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                em.set_thumbnail(
                    url=f"http://i.ytimg.com/vi/{track['info']['identifier']}/hqdefault.jpg")

                em.add_field(name='Author', value=track['info']['author'])
                if track['info']['isStream']:
                    duration = 'Live'
                else:
                    duration = lavalink.format_time(
                        track['info']['length']).lstrip('00:')

                em.add_field(name='Duration', value=duration)
                try:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                except:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
                em.timestamp = datetime.datetime.utcnow()
                msg = await ctx.send(embed=em)
                await player.set_volume(self.volume)
                if not player.is_playing:
                    await player.play()
                    await player.reset_equalizer()
                    await msg.delete(delay=1)
                    # await self.now(ctx)
                    # return await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))
                    return

        except lavalink.exceptions.NodeException:
            await ctx.send('Node not found, contacting owner for support...')
            me = await self.bot.fetch_user(587068610237693963)
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            await me.send(f'Please restart the lavalink server, {ctx.author.name} in the server {ctx.guild.name} want\'s to use voice')
            return

    @commands.command(name='playlist', aliases = ['pl'], brief='Play a saved playlist with ;playlist play playlist_name\nSave a playlist by queuing songs and using **;playlist add name**\nShow your playlists with **;playlist show**\nShow the contents of a playlist with **;playlist show name**\nDelete saved playlists with **;playlist remove name**\n(Note: Playlist names are case sensitive)')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def playlist(self, ctx, operation, *, name=None):
        async with ctx.typing():
            cluster = MongoClient('mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/Other?retryWrites=true&w=majority')
            db = cluster.Other
            collection = db['Playlists']
            help_message = 'Play a saved playlist with ;playlist play playlist_name\nSave a playlist by queuing songs and using **;playlist add name**\nShow your playlists with **;playlist show**\nShow the contents of a playlist with **;playlist show name**\nDelete saved playlists with **;playlist remove name**\n(Note: Playlist names are case sensitive)'
            if operation.lower() in ['show','list']:
 
                if name == None:
                    playlists = collection.find({'id':ctx.author.id})
                    if playlists == None:
                        return await ctx.send('You have no saved playlists')
                    string = '**'
                    for playlist in playlists:
                        # ten = ''
                        # num = 0
                        # numsong = len(playlist['songs'])
                        # if numsong > 10:
                        #     numsong = 10
                        # while num < numsong:
                        #     ten += playlist['songs'][num]['info']['title']
                        #     ten += '\n'
                        #     ten += playlist['songs'][num]['info']['uri']
                        #     ten += '\n\n'
                        #     num += 1
                        # ten += f"And {len(playlist['songs'])-numsong} more song(s)..."
                        # embed.add_field(name=f"{playlist['name']}",value=ten)
                        string += str(playlist['name'])
                        string += '\n'
                    string += '**'
                    embed = discord.Embed(title=f'Playlists for {ctx.author.display_name}', color=random.randint(0,0xffffff), description=string)
                    try:
                        embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                    except:
                        embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
                    
                    embed.timestamp = datetime.datetime.utcnow()
                    return await ctx.send(embed=embed)
                else:
                    
                    playlist = collection.find_one({'id':ctx.author.id,'name':name})
                    if playlist == None:
                        return await ctx.send(f'You have no playlists with the name `{name}`')
                    # songs = ''
                    # for song in playlist['songs']:
                    #     songs += song['info']['title']
                    #     songs += '\n'
                    #     songs += song['info']['uri']
                    #     songs += '\n\n'
                
                    menu1 = menu(source=Playlist(ctx, playlist['songs'],ctx.author.display_name,name))

                    return await menu1.start(ctx)

                    # embed = discord.Embed(title=f'Playlist `{name}` for {ctx.author.display_name}', description = songs, color=random.randint(0,0xffffff))
                    # embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                    # embed.timestamp = datetime.datetime.utcnow()
                    # return await ctx.send(embed=embed)

            if name == None:
                return await ctx.send(help_message)
            if operation.lower() in ['play','start']:
                player = self.bot.lavalink.player_manager.get(ctx.guild.id)
                playlist = collection.find_one({'id':ctx.author.id,'name':name})
                if playlist == None:
                    return await ctx.send(f'You have no playlists with the name `{name}`')
                for song in playlist['songs']:
                    player.add(requester=song['requester'], track=song)
                em = discord.Embed(color = random.randint(0,0xffffff))
                try:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                except:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
                
                em.timestamp = datetime.datetime.utcnow()
                em.title = 'Playlist Enqueued!'
                em.description = f"{playlist['name']} - {len(playlist['songs'])} tracks"
                msg = await ctx.send(embed=em)
                await player.set_volume(self.volume)

                if player.fetch(ctx.guild.id) != None:
                    player.delete(ctx.guild.id)
                player.store(ctx.guild.id, ctx.message.channel.id)
                await ctx.send(f'Sending now playing messages in **{ctx.channel.name}**')

                if not player.is_playing:
                    await player.play()
                    await player.reset_equalizer()
                    await msg.delete(delay=1)
                    # await self.now(ctx)
                    # return await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))
                    return
                return

            elif operation.lower() in ['save', 'add']:
                player = self.bot.lavalink.player_manager.get(ctx.guild.id)
                songs = []

                if len(player.queue)==0 and not player.is_playing():
                    return await ctx.send('Queue is empty and nothing is playing, so there is nothing to save! Add songs to the queue with ;play')
                playlist = collection.find_one({'id':ctx.author.id,'name':name})
                if playlist != None:
                    await ctx.send(f'There is already a playlist that you have saved named **{name}**, type yes to override the saved playlist or type no to stop')
                    
                    def check(m):
                        return m.author.id == ctx.author.id
                    try:
                        response = await self.bot.wait_for('message', check=check, timeout=120)
                    except asyncio.TimeoutError:
                        return await ctx.send('Timed out after 120 seconds, cancelling')
                    if response.content.lower() in ['y','yes']:
                        await ctx.send('Overriding the old playlist')
                        collection.find_one_and_delete({'id':ctx.author.id,'name':name})
                    else:
                        return await ctx.send('Cancelling the override')


                if player.current:
                    song = player.current
                    newsong = {'info':{}}
                    newsong['track'] = song['track']
                    newsong['info']['identifier'] = song['identifier']
                    newsong['info']['isSeekable'] = song['is_seekable']
                    newsong['info']['author'] = song['author']
                    newsong['info']['length'] = song['duration']
                    newsong['info']['isStream'] = song['stream']
                    newsong['info']['title'] = song['title']
                    newsong['info']['uri'] = song['uri']
                    newsong['requester'] = song['requester']
                    songs.append(newsong)
                for song in player.queue:
                    newsong = {'info':{}}
                    newsong['track'] = song['track']
                    newsong['info']['identifier'] = song['identifier']
                    newsong['info']['isSeekable'] = song['is_seekable']
                    newsong['info']['author'] = song['author']
                    newsong['info']['length'] = song['duration']
                    newsong['info']['isStream'] = song['stream']
                    newsong['info']['title'] = song['title']
                    newsong['info']['uri'] = song['uri']
                    newsong['requester'] = song['requester']
                    songs.append(newsong)
                
                collection.insert_one({'id':ctx.author.id,'songs':songs,'name':name})
                return await ctx.send(f'Saved playlist **{name}** with **{len(player.queue)+1}** songs')

            elif operation.lower() in ['remove','delete']:
                playlist = collection.find_one_and_delete({'id':ctx.author.id,'name':name})
                if playlist == None:
                    return await ctx.send(f'You have not saved a playlist named **{name}**')
                else:
                    return await ctx.send(f'Deleted playlist **{name}**')
            else:
                return await ctx.send(help_message)

    @commands.command(name='seek', brief='Seeks to a point in the song (positive seconds moves the song forward that much while negative seconds moves the song backward that much')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def seek(self, ctx, seconds: str=None):
        is1 = seconds.find(':')
        if str(is1) == '-1':
            second = seconds

        else:
            secondsplit = seconds.split(":")
            types = len(secondsplit)

            if types == 2:
                second = int(secondsplit[0]) * 60
                second += int(secondsplit[1])

            elif types == 3:
                second = int(secondsplit[0]) * 3600
                second += int(secondsplit[1]) * 60
                second += int(secondsplit[2])

            else:
                return await ctx.send('Please format your time like this 1:35:54 for 1 hour, 35 minutes and 54 seconds or 35:54 for 35 minutes and 54 seconds, or 54 for 54 seconds')
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')

        if not seconds:
            return await ctx.send('You need to specify the amount of seconds to seek :fast_forward:')
        try:
            track_time = player.position + int(second) * 1000
            await player.seek(int(track_time))
        except ValueError:
            return await ctx.send('Specify valid amount of seconds :clock3:')

        return await ctx.send(f'Moved track to **{lavalink.format_time(track_time)}**')


    @commands.command(name='skip', brief='Skips the song playing')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')

        await ctx.send('⏭ Skipped')
        await player.skip()
        return

    @commands.command(name='nowplaying', aliases=['current', 'playing', 'np'], brief='Shows the song that is playing')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
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
            em.add_field(name='Author', value=f'{player.current.author}')
            if player.repeat:
                em.add_field(name='Queue Loop', value=f'On')
            else:
                em.add_field(name='Queue Loop', value=f'Off')
            em.add_field(name='Volume', value=f'{player.volume}%')
            em.set_author(name="Now Playing 🎵",
                          icon_url="https://i.ibb.co/DGsmTvh/star.gif")
            em.set_thumbnail(
                url=f"http://i.ytimg.com/vi/{player.current.identifier}/hqdefault.jpg")
            requester = ctx.guild.get_member(player.current.requester)
            try:
                em.set_footer(
                text=f"Requested by: {requester}", icon_url=requester.avatar.url)
            except:
                em.set_footer(
                text=f"Requested by: {requester}", icon_url=requester.default_avatar.url)
            em.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=em)
            # return await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=player.current.title))
            return
        else:
            return await ctx.send('Not playing anything :mute:')

    @commands.command(name='save', aliases=['star'], brief='Saves the song playing to your dm')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def savetodm(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.current:
            if player.current.stream:
                dur = 'Live'
            else:
                dur = lavalink.format_time(
                    player.current.duration).lstrip('00:')
            song = f'[{player.current.title}]({player.current.uri})'
            em = discord.Embed(colour=discord.Color(random.randint(0,0xffffff)), description=song)
            em.set_author(name="Saved Song 🎵",
                          icon_url="https://i.ibb.co/DGsmTvh/star.gif")
            em.set_thumbnail(
                url=f"http://i.ytimg.com/vi/{player.current.identifier}/hqdefault.jpg")
            em.add_field(name='Author', value=player.current.author)
            em.add_field(name='Duration', value=dur)
            em.timestamp = datetime.datetime.utcnow()
            user = ctx.author
            await user.send(embed=em)
            await ctx.send(f"Current song has been sent to you {ctx.author.mention} :floppy_disk:")
            return
        else:
            return await ctx.send('Not playing anything :mute:')

    @commands.command(name='queue', aliases=['q'], brief='Checks the queue for songs')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def queue(self, ctx, page: int = 1):
        async with ctx.typing():
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)
            
            if not player.queue:
                return await ctx.send('Queue empty! :cd:')
            menu1 = menu(source=HelpMenu(ctx, self.bot, player.queue))

            return await menu1.start(ctx)
            # items_per_page = 10
            # pages = math.ceil(len(player.queue) / items_per_page)

            # start = (page - 1) * items_per_page
            # end = start + items_per_page

            # queue_list = ''

            # for i, track in enumerate(player.queue[start:end], start=start):
            #     queue_list += f'`{i + 1}.` [{track.title}]({track.uri})\n'

            # embed = discord.Embed(color=random.randint(0,0xffffff),
            #                     description=f'**{len(player.queue)} tracks**\n\n{queue_list}')
            # embed.set_footer(text=f'Viewing page {page}/{pages}')
            # embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
            # embed.timestamp = datetime.datetime.utcnow()
            # return await ctx.send(embed=embed)

    @commands.command(name='resume', aliases=['r'], brief='Resumes the song')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
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
    @commands.cooldown(times, cooldown, commands.BucketType.user)
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
    async def _volume(self, ctx, volume: int = None):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if volume == None:
            return await ctx.send(f'🔈 The volume is at {player.volume}%')
        if volume > 100 and str(ctx.author.id) != '587068610237693963':
            return await ctx.send('Saving eardrums, ask owner for override over 100 percent volume')
        await player.set_volume(volume)
        self.volume = volume
        return await ctx.send(f'🔈 Set to {player.volume}%')

    @commands.command(name='shuffle', brief='Shuffles the queue')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def shuffle(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')
        random.shuffle(player.queue)

        return await ctx.send('🔀 Shuffled the queue')



        # player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # if not player.is_playing:
        #     return await ctx.send('Not playing anything :mute:')

        # player.shuffle = not player.shuffle

        # return await ctx.send('🔀 Shuffle ' + ('enabled' if player.shuffle else 'disabled'))

    @commands.command(name='loop', brief='Loops/repeats the current queue')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def loop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')

        player.repeat = not player.repeat

        return await ctx.send('Queue Loop ' + ('enabled' if player.repeat else 'disabled'))

    @commands.command(name='remove', brief='Removes a song from a queue')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def remove(self, ctx, index: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('Nothing queued :cd:')

        if index > len(player.queue) or index < 1:
            return await ctx.send('Index has to be greater than 0 and less than or equal to the queue size')

        index = index - 1
        removed = player.queue.pop(index)

        return await ctx.send('Removed **' + removed.title + '** from the queue')

    @commands.command(name='skipto', brief='Skips to a song in queue')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def skipto(self, ctx, index: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Not playing anything :mute:')
        player.queue = player.queue[index-1:]
        await player.skip()
        return await ctx.send(f"⏭ Skipped to {player.current.title}")

    @commands.command(name='leave', aliases=['stop', 'dc', 'disconnect', 'end'], brief='Makes the bot leave the channel it is in, clear the queue and stop playing')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def disconnect(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            # We can't disconnect, if we're not connected.
            return await ctx.send('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            # Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot
            # may not disconnect the bot.
            return await ctx.send('You\'re not in my voicechannel!')

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await ctx.voice_client.disconnect(force=True)
        return await ctx.send('Disconnected')
        

    @commands.command(aliases=['qc','cq', 'clearq', 'qclear'], brief='Clears all the songs in the queue')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def queueclear(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        num = len(player.queue)
        player.queue.clear()
        return await ctx.send(f'Cleared {num} songs from the queue')

    # @commands.command(name='lyrics', aliases=['ly'], brief='Get the lyrics of a song, if the lyrics given are incorrect, use the searchlyrics command')
    # @commands.cooldown(times, cooldown, commands.BucketType.user)
    # async def get_lyrics(self, ctx, *, query: str = ""):
    #     if not query:
    #         player = self.bot.lavalink.player_manager.get(ctx.guild.id)

    #         if not player.is_playing:
    #             return await ctx.send('I\'m not currently playing anything :warning:')
    #         query = player.current.title

    #     try:
    #         async with ctx.typing():
    #             results = await self.kclient.music.lyrics(query, limit=1)
    #     except ksoftapi.NoResults:
    #         await ctx.send(f'No lyrics found for `{query}`')
    #     else:
    #         lyrics = results[0].lyrics
    #         result = results[0]
    #         embed = discord.Embed(title=f'{result.name} - {result.artist}',
    #                               color=random.randint(0,0xffffff), description=lyrics[:2048])
    #         embed.set_thumbnail(url=result.album_art)
    #         embed.set_author(name="Lyrics:")
    #         embed.timestamp = datetime.datetime.utcnow()
    #         lyrics = lyrics[2048:]
    #         embeds = [embed]  # create embeds' list for long lyrics
    #         while len(lyrics) > 0 and len(embeds) < 10:  # limiting embeds to 10
    #             embed = discord.Embed(color=random.randint(0,0xffffff), description=lyrics[:2048])
    #             lyrics = lyrics[len(embeds)*2048:]
    #             embed.timestamp = datetime.datetime.utcnow()
    #             embeds.append(embed)
    #         # set footer for last embed
    #         embeds[-1].set_footer(text="Source: KSoft.Si")
    #         for embed in embeds:
    #             await ctx.send(embed=embed)
            
    #         return

    # @commands.command(name='searchlyrics', aliases=['sly'], brief='Get the lyrics of a song, but with multiple options given')
    # @commands.cooldown(times, cooldown, commands.BucketType.user)
    # async def searchly(self, ctx, number: Optional[int]=3, *, query: str = ""):
    #     if number > 10:
    #         return await ctx.send('The amount of lyrics cannot exceed 10')
    #     if not query:
    #         player = self.bot.lavalink.player_manager.get(ctx.guild.id)

    #         if not player.is_playing:
    #             return await ctx.send('I\'m not currently playing anything :warning:')
    #         query = player.current.title

    #     try:
    #         async with ctx.typing():
    #             Results = await self.kclient.music.lyrics(query, limit=number)
    #     except ksoftapi.NoResults:
    #         await ctx.send(f'No lyrics found for `{query}`')
    #     else:
    #         embed = discord.Embed(title=f'Lyrics for the Song `{query}`', description='React with the number to get the lyrics for that song', color=random.randint(0,0xffffff))
    #         try:
    #             embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    #         except:
    #             embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.default_avatar.url)
    #         timestamp = datetime.datetime.utcnow()
    #         embed.timestamp = timestamp
    #         for i in range(len(Results)):
    #             embed.add_field(name=f'{i+1})', value=f'{Results[i].name}-{Results[i].artist}', inline=False)
    #         msg = await ctx.send(embed=embed)
    #         reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣',
    #                 '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    #         for i in range(len(Results)):
    #             await msg.add_reaction(reactions[i])
    #         def check(reaction,user):
    #             return user == ctx.author and reaction.emoji in reactions and reaction.message == msg
    #         try:
    #             reaction,user = await self.bot.wait_for('reaction_add', check=check, timeout=20)
    #         except asyncio.TimeoutError:
    #             return await ctx.send("Timed out please try again")
    #         em = reactions.index(reaction.emoji)
    #         lyrics = Results[em].lyrics
    #         result = Results[em]
    #         embed = discord.Embed(title=f'{result.name} - {result.artist}',
    #                             color=random.randint(0,0xffffff), description=lyrics[:2048])
    #         embed.set_thumbnail(url=result.album_art)
    #         embed.set_author(name="Lyrics:")
    #         embed.timestamp = datetime.datetime.utcnow()
    #         lyrics = lyrics[2048:]
    #         embeds = [embed]  # create embeds' list for long lyrics
    #         while len(lyrics) > 0 and len(embeds) < 10:  # limiting embeds to 10
    #             embed = discord.Embed(color=random.randint(0,0xffffff), description=lyrics[:2048])
    #             lyrics = lyrics[len(embeds)*2048:]
    #             embed.timestamp = datetime.datetime.utcnow()
    #             embeds.append(embed)
    #         # set footer for last embed
    #         embeds[-1].set_footer(text="Source: KSoft.Si")
    #         for embed in embeds:
    #             await ctx.send(embed=embed)
            
    #         return

    @commands.command(name='equalizer', aliases=['eq'], brief='Change frequencies')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def equalizer(self, ctx, *args):
        """Equalizer"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if len(args) == 0:
            await ctx.send('Note: specify `band gain` or `preset` to change frequencies :control_knobs:')
        elif len(args) == 1:
            presets = {
                'reset': 'Default',
                'bassboost': [0.08, 0.12, 0.2, 0.18, 0.15, 0.1, 0.05, 0.0, 0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14],
                'negative_hertz': [0.08, 0.12, 0.2, 0.18, 0.15, 0.1, 0.05, 0.0, 0.02, -0.08, -0.12, -0.16, -0.20, -0.24, -0.25],
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

            elif preset == 'list':
                em = discord.Embed(title=':control_knobs: EQ presets:', color=random.randint(0,0xffffff), description='\n'.join(presets.keys()))
                try:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
                except:
                    em.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.default_avatar.url)
                em.timestamp = datetime.datetime.utcnow()
                return await ctx.send(embed=em)
            else:
                return await ctx.send('Invalid preset specified \nType `;eq list` for all presets')
        elif len(args) == 2:
            try:
                band = int(args[0])-1
                gain = float(args[1])
                await player.set_gain(band, gain)
            except ValueError:
                return await ctx.send('Specify valid `band gain` values :control_knobs:')
        else:
            return await ctx.send('Specify `band gain` or `preset` :control_knobs:')
        # Print final EQ settings
        eq_frequencies = [f"`{gain}`" for gain in player.equalizer]
        return await ctx.send("Current Values:\n" + ' '.join(eq_frequencies))


async def setup(bot):
    await bot.add_cog(music(bot))
