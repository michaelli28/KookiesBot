import asyncio
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
import discord
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from discord.ext import commands
from typing import Optional
#import pyprog
from time import sleep
from pytz import timezone
import aiohttp
from googleapiclient.discovery import build
#TODO PLAYLIST CMD
youtube_dl.utils.bug_reports_message = lambda: ''
ydl = youtube_dl.YoutubeDL({"format": "bestaudio/best", "restrictfilenames": True, "noplaylist": True, "nocheckcertificate": True,
                            "ignoreerrors": True, "logtostderr": False, "quiet": True, "no_warnings": True, "source_address": "0.0.0.0"})

APIKEY = 'AIzaSyB1cW7goiUiwUaC044lec_0hHC6ba2N-HI'

class EmptyQueue(Exception):
    """Cannot skip because queue is empty"""


class NotConnectedToVoice(Exception):
    """Cannot create the player because bot is not connected to voice"""


class NotPlaying(Exception):
    """Cannot <do something> because nothing is being played"""


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        self.place = 1
        super().__init__(data, per_page=10)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(
            title=f"Music Queue For {self.ctx.guild.name}", color=random.randint(0, 0xffffff))
        embed.set_thumbnail(url=self.ctx.guild.me.avatar.url)
        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} songs")
        timestamp = datetime.datetime.utcnow()
        embed.timestamp = timestamp
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        n = (menu.current_page)*10+1
        for entry in entries:
            try:
                fields.append((f'{n})', f'[{entry.name}]({entry.url})'))
            except:
                pass
            n+=1
        self.place += 1

        return await self.write_page(menu, fields)

def parse_duration(duration: int):
    if duration > 0:
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{}'.format(days))
        if hours > 0:
            if len(str(hours)) == 1:
                hours = '0' + str(hours)
            duration.append('{}'.format(hours))
        else:
            pass
        if minutes > 0:
            if len(str(minutes)) == 1:
                minutes = '0' + str(minutes)
            duration.append('{}'.format(minutes))
        else:
            duration.append('00')
        if seconds > 0:
            if len(str(seconds)) == 1:
                seconds = '0' + str(seconds)
            duration.append('{}'.format(seconds))
        else:
            duration.append('00')

        value = ':'.join(duration)

    elif duration == 0:
        value = "LIVE"

    return value


async def ytbettersearch(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
            #print(html)
    index = html.find('watch?v')
    url = ""
    while True:
        char = html[index]
        if char == '"':
            break
        url += char
        index += 1
    url = f"https://www.youtube.com/{url}"
    # headers = {'User-Agent': 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'}

    # async with httpx.AsyncClient() as client:
    #     response = await client.get(f'https://www.youtube.com/results?search_query={query}', headers=headers)
    #     print(response.text)
    #     print(url)
    #     urlB = re.findall('"url":"/watch\?v=(.*?)\\u0026list=', response.text)
    # if len(urlB) == 0:
    #     return None
    # else:
    #     url1 = f'https://www.youtube.com/watch?v={urlB[0]}'
    #     print('###############################################################################################3######')
    #     print(url1)
    return url


async def get_video_data(url, search, bettersearch, loop, ctx):
    if not search and not bettersearch:
        data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        source = data["url"]
        url = "https://www.youtube.com/watch?v="+data["id"]
        title = data["title"]
        description = data["description"]
        # likes = data["like_count"]
        # dislikes = data["dislike_count"]
        date = data['upload_date']
        views = data["view_count"]
        duration = data["duration"]
        thumbnail = data["thumbnail"]
        channel = data["uploader"]
        channel_url = data["uploader_url"]
        return Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False, ctx, date)
    else:
        if bettersearch:
            url = await ytbettersearch(url)
            if url ==None:
                return await ctx.send(f'No results for search: {url}')
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            try:
                data = data["entries"][0]
            except KeyError:
                pass
            except TypeError:
                pass
            source = data["url"]
            url = "https://www.youtube.com/watch?v="+data["id"]
            title = data["title"]
            description = data["description"]
            # likes = data["like_count"]
            # dislikes = data["dislike_count"]
            date = data['upload_date']
            views = data["view_count"]
            duration = data["duration"]
            thumbnail = data["thumbnail"]
            channel = data["uploader"]
            channel_url = data["uploader_url"]
            return Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False, ctx, date)

        elif search:
            ytdl = youtube_dl.YoutubeDL({"format": "bestaudio/best", "restrictfilenames": True, "noplaylist": True, "nocheckcertificate": True,
                                         "ignoreerrors": True, "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto", "source_address": "0.0.0.0"})
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            try:
                data = data["entries"][0]
            except TypeError:
                pass
            except KeyError:
                pass
            del ytdl
            try:
                source = data["url"]
            except Exception as e:
                print(url)
                return
            url = "https://www.youtube.com/watch?v="+data["id"]
            title = data["title"]
            description = data["description"]
            # likes = data["like_count"]
            # dislikes = data["dislike_count"]
            date = data['upload_date']
            views = data["view_count"]
            duration = data["duration"]
            thumbnail = data["thumbnail"]
            channel = data["uploader"]
            channel_url = data["uploader_url"]
            return Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False, ctx, date)


def check_queue(ctx, opts, music, after, on_play, loop, volume):
    try:
        song = music.queue[ctx.guild.id][0]
    except IndexError:
        return
    if not song.is_looping:
        try:
            music.queue[ctx.guild.id].pop(0)
        except IndexError:
            return
        if len(music.queue[ctx.guild.id]) > 0:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                music.queue[ctx.guild.id][0].source, **opts))
            try:
                ctx.voice_client.play(source, after=lambda error: after(
                ctx, opts, music, after, on_play, loop, volume))
            except TypeError:
                pass
            ctx.voice_client.source.volume = volume
            song = music.queue[ctx.guild.id][0]
            # if song == None:
            #     pass
            # else:
            #     msg = await ctx.send(embed=song.create_embed())
            #     await msg.add_reaction('⏯️')
            #     await msg.add_reaction('⏩')
            #     await msg.add_reaction('🔁')
            #     #await msg.add_reaction('🔀')
            #     await msg.add_reaction('⏹️')
            #     await msg.add_reaction('🔈')
            #     await msg.add_reaction('🔊')
            if on_play:
                loop.create_task(on_play(ctx, song))
    else:
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            music.queue[ctx.guild.id][0].source, **opts))
        try:
            ctx.voice_client.play(source, after=lambda error: after(
            ctx, opts, music, after, on_play, loop, volume))
        except TypeError:
            pass
        ctx.voice_client.source.volume = volume
        song = music.queue[ctx.guild.id][0]
        # if song == None:
        #     pass
        # else:
        #     msg = await ctx.send(embed=song.create_embed())
        #     await msg.add_reaction('⏯️')
        #     await msg.add_reaction('⏩')
        #     await msg.add_reaction('🔁')
        #     #await msg.add_reaction('🔀')
        #     await msg.add_reaction('⏹️')
        #     await msg.add_reaction('🔈')
        #     await msg.add_reaction('🔊')
        if on_play:
            loop.create_task(on_play(ctx, song))


class Musicclass:
    def __init__(self):
        self.queue = {}
        self.players = []

    def create_player(self, ctx, **kwargs):
        if not ctx.voice_client:
            raise NotConnectedToVoice(
                "Cannot create the player because bot is not connected to voice")
        player = MusicPlayer(ctx, self, **kwargs)
        self.players.append(player)
        return player

    def get_player(self, **kwargs):
        guild = kwargs.get("guild_id")
        channel = kwargs.get("channel_id")
        for player in self.players:
            if guild and channel and player.ctx.guild.id == guild and player.voice.channel.id == channel:
                return player
            elif not guild and channel and player.voice.channel.id == channel:
                return player
            elif not channel and guild and player.ctx.guild.id == guild:
                return player
        else:
            return None


class MusicPlayer:
    def __init__(self, ctx, music, **kwargs):
        self.ctx = ctx
        self.voice = ctx.voice_client
        self.loop = ctx.bot.loop
        self.music = music
        self.volume = 0.10
        if self.ctx.guild.id not in self.music.queue.keys():
            self.music.queue[self.ctx.guild.id] = []

        self.after_func = check_queue
        self.on_play_func = self.on_queue_func = self.on_skip_func = self.on_stop_func = self.on_pause_func = self.on_resume_func = self.on_loop_toggle_func = self.on_volume_change_func = self.on_remove_from_queue_func = None

        ffmpeg_error = kwargs.get(
            "ffmpeg_error_betterfix", kwargs.get("ffmpeg_error_fix"))
        if ffmpeg_error and "ffmpeg_error_betterfix" in kwargs.keys():
            self.ffmpeg_opts = {"options": "-vn -loglevel quiet -hide_banner -nostats",
                                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin"}
        elif ffmpeg_error:
            self.ffmpeg_opts = {
                "options": "-vn", "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin"}
        else:
            self.ffmpeg_opts = {"options": "-vn", "before_options": "-nostdin"}

    def disable(self):
        self.music.players.remove(self)

    def on_queue(self, func):
        self.on_queue_func = func

    def on_play(self, func):
        self.on_play_func = func

    def on_skip(self, func):
        self.on_skip_func = func

    def on_stop(self, func):
        self.on_stop_func = func

    def on_pause(self, func):
        self.on_pause_func = func

    def on_resume(self, func):
        self.on_resume_func = func

    def on_loop_toggle(self, func):
        self.on_loop_toggle_func = func

    def on_volume_change(self, func):
        self.on_volume_change_func = func

    def on_remove_from_queue(self, func):
        self.on_remove_from_queue_func = func

    async def queue(self, url, search=False, bettersearch=True):
        song = await get_video_data(url, search, bettersearch, self.loop, self.ctx)
        self.music.queue[self.ctx.guild.id].append(song)
        if self.on_queue_func:
            await self.on_queue_func(self.ctx, song)

        return song

    async def play(self):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            self.music.queue[self.ctx.guild.id][0].source, **self.ffmpeg_opts))
        try:
            self.voice.play(source, after=lambda error: self.after_func(
            self.ctx, self.ffmpeg_opts, self.music, self.after_func, self.on_play_func, self.loop, self.volume))
        except TypeError:
            pass
        self.voice.source.volume = self.volume
        song = self.music.queue[self.ctx.guild.id][0]
        if song == None:
            pass
        else:
            msg = await self.ctx.send(embed=song.create_embed())
            await msg.add_reaction('⏯️')
            await msg.add_reaction('⏩')
            await msg.add_reaction('🔁')
            #await msg.add_reaction('🔀')
            await msg.add_reaction('⏹️')
            await msg.add_reaction('🔈')
            await msg.add_reaction('🔊')
        if self.on_play_func:
            await self.on_play_func(self.ctx, song)
        return song


    async def skip(self, force=False):
        if len(self.music.queue[self.ctx.guild.id]) == 0:
            raise NotPlaying("Cannot loop because nothing is being played")
        elif not len(self.music.queue[self.ctx.guild.id]) > 1 and not force:
            raise EmptyQueue("Cannot skip because queue is empty")
        else:
            old = self.music.queue[self.ctx.guild.id][0]
            old.is_looping = False if old.is_looping else False
            self.voice.stop()
            try:
                new = self.music.queue[self.ctx.guild.id][0]
                if self.on_skip_func:
                    await self.on_skip_func(self.ctx, old, new)
                return (old, new)
            except IndexError:
                if self.on_skip_func:
                    await self.on_skip_func(self.ctx, old)
                return old

    async def stop(self):
        try:
            self.music.queue[self.ctx.guild.id] = []
            self.voice.stop()
            self.music.players.remove(self)
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        if self.on_stop_func:
            await self.on_stop_func(self.ctx)

    async def pause(self):
        try:
            self.voice.pause()
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot pause because nothing is being played")
        if self.on_pause_func:
            await self.on_pause_func(self.ctx, song)
        return song

    async def resume(self):
        try:
            self.voice.resume()
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot resume because nothing is being played")
        if self.on_resume_func:
            await self.on_resume_func(self.ctx, song)
        return song

    def current_queue(self):
        try:
            return self.music.queue[self.ctx.guild.id]
        except KeyError:
            raise EmptyQueue("Queue is empty")

    def now_playing(self):
        try:
            return self.music.queue[self.ctx.guild.id][0]
        except:
            return None

    async def toggle_song_loop(self):
        try:
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        if not song.is_looping:
            song.is_looping = True
        else:
            song.is_looping = False
        if self.on_loop_toggle_func:
            await self.on_loop_toggle_func(self.ctx, song)
        return song

    async def change_volume(self, vol):
        self.voice.source.volume = vol
        try:
            song = self.music.queue[self.ctx.guild.id][0]
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        if self.on_volume_change_func:
            await self.on_volume_change_func(self.ctx, song, vol)
        return (song, vol)

    async def remove_from_queue(self, index):
        if index == 0:
            try:
                song = self.music.queue[self.ctx.guild.id][0]
            except:
                raise NotPlaying("Cannot loop because nothing is being played")
            await self.skip(force=True)
            return song
        song = self.music.queue[self.ctx.guild.id][index]
        self.music.queue[self.ctx.guild.id].pop(index)
        if self.on_remove_from_queue_func:
            await self.on_remove_from_queue_func(self.ctx, song)
        return song

    def delete(self):
        self.music.players.remove(self)


class Song:
    def __init__(self, source, url, title, description, views, duration, thumbnail, channel, channel_url, loop, ctx, date):
        self.source = source
        self.url = url
        self.title = title
        self.description = description
        self.views = views
        self.name = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.channel = channel
        self.channel_url = channel_url
        self.is_looping = loop
        self.ctx = ctx
        self.date = date
        #self.volume = self.ctx.voice_client.source.volume or self.ctx.voice_client.volume

    def create_embed(self):
        date = datetime.datetime.strptime(self.date, '%Y%m%d')
        date = f'{date.month}/{date.day}/{date.year}'
        embed = (discord.Embed(title='Now playing', description='```css\n{0.name}\n```'.format(self), color=random.randint(0, 0xffffff))
                    .add_field(name='Duration', value=parse_duration(self.duration))
                    .add_field(name='Requested by', value=self.ctx.author.mention)
                    .add_field(name='Volume', value=f'**{self.ctx.voice_client.source.volume*100}**%')
                    .add_field(name='Uploader', value='[{0.channel}]({0.channel_url})'.format(self))
                    .add_field(name='URL', value='[Click]({0.url})'.format(self))
                    .add_field(name='Date', value=f'{date}')
                    .set_thumbnail(url=self.thumbnail)
                    .set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url))
        embed.timestamp = datetime.datetime.utcnow()
        return embed


musicstart = Musicclass()

class music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx):
        self.ctx = ctx

    @commands.command(name='join', aliases=['j'], brief='Makes the bot join a voice channel')
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
        if ctx.voice_client:
            await ctx.voice_client.move_to(destination)
            return await ctx.send(f'{ctx.author.mention}, connected to: **{destination}**, type **;leave** to leave the channel')
        else:    
            await destination.connect()
            return await ctx.send(f'{ctx.author.mention}, connected to: **{destination}**, type **;leave** to leave the channel')

    @commands.command(name='leave', aliases=['disconnect'], brief='Makes the bot leave the channel it is in')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _leave(self, ctx):
        """Clears the queue and leaves the voice channel"""
        # await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')
        #ctx.voice_client.cleanup()
        await ctx.voice_client.disconnect()
        
        return await ctx.send('Left **' + str(vc.channel.name) + '**')

    @commands.command(name='play', brief='Plays or queues a song or playlist by link or by search')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx, *, search: str=None):
        
        if search == None:
            return await ctx.send(f'{ctx.author.mention}, you need to input a url or search')
        async with ctx.typing():

            voiceconnect = get(ctx.bot.voice_clients, guild=ctx.guild)
            if not voiceconnect or not voiceconnect.is_connected():
                await ctx.invoke(self._join)
            
            player = musicstart.get_player(guild_id=ctx.guild.id)
            if not player:
                player = musicstart.create_player(ctx, ffmpeg_error_betterfix=True)
            httpS = re.findall('www.',search)
            pList = re.findall('list=',search)
            indexL = re.findall('index=',search)
            watch = re.findall('watch',search)
            playlistCheck = re.findall('playlist', search)

            if len(httpS) > 0 and len(pList) > 0 and len(playlistCheck) > 0:
                if len(indexL) == 0 and len(watch) == 0:
                    maxPlaylistSize = 40
                    showVidSize = None
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'}

                    async with httpx.AsyncClient() as client:
                        response = await client.get(search, headers=headers)
                        playlist_urls = re.findall(
                        'watch\?v=(.*?)\\\\u0026list=', response.text)

                    if len(playlist_urls) >= maxPlaylistSize:
                        showVidSize = maxPlaylistSize
                    else:
                        showVidSize = len(playlist_urls)

                    await ctx.send('Putting songs into the queue, please wait a minute or two before checking the queue')
                    
                    for n in range(showVidSize):
                        await player.queue('https://www.youtube.com/watch?v=' + playlist_urls[n], search=True, bettersearch=False)
                        if n==0:
                            if not ctx.voice_client.is_playing():
                                await player.play()
                    return

                elif len(watch) > 0:
                    response = requests.get(search)
                    soup = BeautifulSoup(response.text, 'lxml')
                    playlistUrls = re.findall(
                        '"url":"/watch\?v=(.*?)"', soup.prettify())
                    playlistUrls2 = []

                    for url in playlistUrls:
                        url2 = re.findall('(.*?)\\\\u0026list=', url)

                        if len(url2) > 0:
                            playlistUrls2.append(url2[0])
                        else:
                            playlistUrls2.append(url)
                    res = [i for n, i in enumerate(playlistUrls2) if i not in playlistUrls2[:n]]
                    maxPlaylistSize = 40
                    showVidSize = None

                    if len(res) >= maxPlaylistSize:
                        showVidSize = maxPlaylistSize
                    else:
                        showVidSize = len(res)


                    await ctx.send(f'{ctx.author.mention}, putting songs into the queue, please wait a minute or two before checking the queue')

                    for n in range(showVidSize):
                        await player.queue('https://www.youtube.com/watch?v=' + res[n], search=True, bettersearch=False)
                        if n == 0:
                            if not ctx.voice_client.is_playing():
                                await player.play()
                    return

                elif len(httpS)>0 and len(pList) < 0:
                    return await ctx.send('Please format your link like this: https://www.youtube.com/playlist?list=woie392osf83298 for playlists')

                elif len(httpS)>0 and len(playlistCheck) < 0:
                    return await ctx.send('Please format your link like this: https://www.youtube.com/playlist?list=woie392osf83298 for playlists')

            else:
                if not ctx.voice_client.is_playing():
                    await player.queue(search, bettersearch=True)
                    return await player.play()
                else:
                    song = await player.queue(search, bettersearch=True)
                    return await ctx.send(f"Queued {song.name}")


    @commands.command(name='pause', aliases=['pau'], brief='Pauses the song playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _pause(self, ctx):
        """Pauses the currently playing song"""
        # await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send(f'{ctx.author.mention}, I am not currently playing anything!')

        else:
            player = musicstart.get_player(guild_id=ctx.guild.id)
            await player.pause()

            return await ctx.send(f'{ctx.author.mention} has paused the song!')

    @commands.command(name='resume', aliases=['re', 'res', 'r'], brief='Resumes the song')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _resume(self, ctx):
        """Resumes a currently paused song"""
        # await ctx.message.delete()
        vc = ctx.voice_client
        if not vc.is_playing:
            return await ctx.send(f'{ctx.author.mention}, I am not currently playing anything!')
        if not vc.is_paused:
            return await ctx.send(f'{ctx.author.mention}, song is not paused')
        player = musicstart.get_player(guild_id=ctx.guild.id)
        await player.resume()
        return await ctx.send(f'{ctx.author.mention} has resumed the song!')

    @commands.command(name='stop', brief='Stops the music, clears the queue, and disconnects the bot from the voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _stop(self, ctx):
        await ctx.send('Are you sure you want to stop the song and delete queues and settings? Reply **y** for yes and **n** for no')
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content.lower() == 'y':
            await ctx.send(f'{ctx.author.mention}, stopping player and clearing queue')
        elif msg.content.lower() == 'n':
            return await ctx.send(f'{ctx.author.mention}, continuing')
        else:
            return await ctx.send(f'{ctx.author.mention}, please reply with **y** or **n** next time, continuing')

        player = musicstart.get_player(guild_id=ctx.guild.id)
        #ctx.voice_client.cleanup()
        await ctx.voice_client.disconnect()
        return await player.stop()

    @commands.command(name='search', brief='Searches for a video and returns the top 10 results')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _search(self, ctx, *, query):
        youtube = build('youtube', 'v3', developerKey=APIKEY)
        req = youtube.search().list(part='snippet',
        q=query,
        type='video',
        maxResults=10)
        voiceconnect = get(ctx.bot.voice_clients, guild=ctx.guild)
        if not voiceconnect or not voiceconnect.is_connected():
            await ctx.invoke(self._join)
        player = musicstart.get_player(guild_id=ctx.guild.id)
        if not player:
            player = musicstart.create_player(ctx, ffmpeg_error_betterfix=True)
        res = req.execute()
        results = re.findall("'title': '(.*?)'",str(res))
        embed = discord.Embed(
            color = random.randint(0, 0xffffff),
            title=f'Search results for {query}'
        )
        embed.set_author(name=self.ctx.author.display_name, icon_url=self.ctx.author.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        if len(results)==0:
            return await ctx.send(f'No results for: {query}')
        i=1
        for result in results:
            resultE = re.sub('&#39;','\'',result)
            resultE = re.sub('&quot;','\"',result)
            embed.add_field(name=str(i)+')',value=(resultE), inline=False)
            i+=1
        await ctx.send('Respond with the number you would like to play or stop to stop', embed=embed)
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content.lower() == 'stop':
            return await ctx.send('Stopping')
        else: 
            url = results[int(msg.content)-int(1)]

        if not ctx.voice_client.is_playing():
            await player.queue(url, search=True, bettersearch=False)
            return await player.play()
        else:
            song = await player.queue(url, search=True, bettersearch=False)
            return await ctx.send(f"Queued {song.name}")

    @commands.command(name='loop', brief='Loops the song/queue currently playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def loop(self, ctx):
        try:
            player = musicstart.get_player(guild_id=ctx.guild.id)
            song = await player.toggle_song_loop()
        except:
            return await ctx.send(f'{ctx.author.mention}, I am not currently playing anything')
        return await ctx.send(f'{ctx.author.mention}, song loop is now turned ' + ('**on**' if song.is_looping else '**off**'))

    @commands.command(name='queue', aliases=['q'], brief='Checks the queue for songs')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def queue(self, ctx):
        async with ctx.typing():
            player = musicstart.get_player(guild_id=ctx.guild.id)
            songs = []
            for song in player.current_queue():
                songs.append(song)
            if len(songs[1:-1]) == 0:
                return await ctx.send('Queue empty')
            menu = MenuPages(source=HelpMenu(ctx, songs[1:-1]),
                                delete_message_after=True)

            return await menu.start(ctx)

    @commands.command(name='now', aliases=['current', 'playing', 'np'], brief='Shows the song that is playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _now(self, ctx):
        # await ctx.message.delete()
        vc = ctx.voice_client
        if not vc:
            return await ctx.send('I am not currently playing anything')
        player = musicstart.get_player(guild_id=ctx.guild.id)
        song = player.now_playing()
        embed = song.create_embed()
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('⏯️')
        await msg.add_reaction('⏩')
        await msg.add_reaction('🔁')
        #await msg.add_reaction('🔀')
        await msg.add_reaction('⏹️')
        await msg.add_reaction('🔈')
        return await msg.add_reaction('🔊')

    @commands.command(name='skip', brief='Skips the song playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _skip(self, ctx):
        # await ctx.message.delete()
        vc = ctx.voice_client
        player = musicstart.get_player(guild_id=ctx.guild.id)
        if not vc or not vc.is_connected():
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')

        else:
            await player.skip(force=True)
            return await ctx.send(f'{ctx.author.mention} has skipped the song!')

    @commands.command(name='volume', aliases=['vol', 'v'], brief='Set the volume of the music')
    async def _volume(self, ctx, *, volume: int = None):
        """Sets the volume of the player"""
        player = musicstart.get_player(guild_id=ctx.guild.id)
        if volume == None:
            return await ctx.send(f'{ctx.author.mention}, current volume is at **{ctx.voice_client.source.volume*100}**%')

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel')

        if 0 > volume or volume > 100:
            return await ctx.send(f'{ctx.author.mention}, volume must be between 0 and 100')
        await player.change_volume(float(volume / 100))
        return await ctx.send(f'{ctx.author.mention} has set the volume to **{volume}**%')

    @commands.command(name='remove', brief='Removes a song from a queue')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _remove(self, ctx, index: int):
        """Removes a song from the queue at a given index"""
        vc = ctx.voice_client
        player = musicstart.get_player(guild_id=ctx.guild.id)
        await player.remove_from_queue(int(index))

        if not vc or not vc.is_connected():
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')
        if len(player.current_queue()) == 0:
            return await ctx.send(f'{ctx.author.mention}, queue is empty')
        elif index > len(player.current_queue()):
            return await ctx.send(f'{ctx.author.mention}, invalid index, number too large')
        else:
            player = musicstart.get_player(guild_id=ctx.guild.id)
            await player.remove_from_queue(int(index))
            return await ctx.send(f'{ctx.author.mention}, removed song number **' + str(index) + '**')


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        msg = reaction.message
        if msg.author.id != self.bot.user.id:
            return
        channel = msg.channel
        if msg.embeds:
            if str(msg.embeds[0].title) != 'Now playing':
                return
        if reaction.emoji=='⏯️':
            ctx = self.ctx
            player = musicstart.get_player(guild_id=ctx.guild.id)
            await msg.remove_reaction(reaction, user)
            if not ctx.voice_client:
                return await channel.send(f'{user.mention}, I am not currently playing anything')
            elif ctx.voice_client.is_playing():
                await player.pause()
                return await channel.send(f'{user.mention} has paused the song!')

            elif ctx.voice_client.is_paused():
                await player.resume()
                return await channel.send(f'{user.mention} has resumed the song!')
        if reaction.emoji=='⏩':
            ctx = self.ctx
            player = musicstart.get_player(guild_id=ctx.guild.id)
            await msg.remove_reaction(reaction, user)
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                return await channel.send(f'{user.mention}, I am not currently in a voice channel!')
            await player.skip(force=True)
            return await channel.send(f'{user.mention} has skipped the song!')
        # if reaction.emoji=='🔀':
        #     ctx = self.ctx
        #     await msg.remove_reaction(reaction, user)
        #     if len(vc.songs) == 0:
        #         return await channel.send(f'{user.mention}, queue is empty')
        #     else:
        #         vc.songs.shuffle()
        #         await channel.send(f'{user.mention} has shuffled the queue')
        if reaction.emoji == '🔁':
            ctx = self.ctx
            player = musicstart.get_player(guild_id=ctx.guild.id)
            await msg.remove_reaction(reaction, user)
            if not ctx.voice_client.is_playing:
                return await channel.send(f'{user.mention}, I am not currently playing anything')
            else:
                song = await player.toggle_song_loop()
                return await channel.send(f'{user.mention}, song loop is now turned ' + ('**on**' if song.is_looping else '**off**'))
            
        if reaction.emoji=='🔈':
            ctx = self.ctx
            await msg.remove_reaction(reaction, user)
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                return await channel.send(f'{user.mention}, I am not currently in a voice channel')
            volume = ctx.voice_client.source.volume*100
            if volume-10 < 0:
                volume = 0
            else:
                volume = volume-10
            ctx.voice_client.source.volume = volume/100
            return await channel.send(f'{user.mention} has set the volume to **{volume}**%', delete_after=10)

        if reaction.emoji=='🔊':
            ctx = self.ctx
            await msg.remove_reaction(reaction, user)
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                return await channel.send(f'{user.mention}, I am not currently in a voice channel')
            volume = ctx.voice_client.source.volume*100
            if volume+10 > 100:
                volume = 100
            else:
                volume = volume+10
            ctx.voice_client.source.volume = volume/100
            return await channel.send(f'{user.mention} has set the volume to **{volume}**%', delete_after=10)

        if reaction.emoji == '⏹️':
            ctx = self.ctx
            await msg.remove_reaction(reaction, user)
            vc = ctx.voice_client
            if not vc or not vc.is_connected():
                return await channel.send(f'{user.mention}, I am not currently in a voice channel!')
            else:
                await channel.send(f'{user.mention}, stopping player and clearing queue')
                player = musicstart.get_player(guild_id=ctx.guild.id)
                return await player.stop()



def setup(bot):
    bot.add_cog(music(bot))
