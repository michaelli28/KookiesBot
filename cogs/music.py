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
from discord.utils import get
from discord.ext import commands
from typing import Optional
#import pyprog
from time import sleep
from pytz import timezone
from cogs.musicmodule import musicmodule
from musicmodule import Song
music = musicmodule.Music()


class songclass(Song):
    def __init__(self, ctx, song, requester):
        super().__init__(song.source, song.url, song.title, song.description, song.views,
                         song.duration, song.thumbnail, song.channel, song.channel_url, song.loop)
        self.ctx = ctx
        self.requester = requester
        self.player = music.get_player(guild_id=ctx.guild.id)

    def create_embed(self, song):
        embed = (discord.Embed(title='Now playing', description='```css\n{0.name}\n```'.format(song), color=random.randint(0, 0xffffff))
                 .add_field(name='Duration', value=song.duration)
                 .add_field(name='Requested by', value=song.requester.mention)
                 .add_field(name='Volume', value=f'**{self.player.volume*100}**%')
                 .add_field(name='Uploader', value='[{0.channel}]({0.channel_url})'.format(song), inline=False)
                 .add_field(name='URL', value='[Click]({0.url})'.format(song))
                 .set_thumbnail(url=song.thumbnail)
                 .set_author(name=song.requester.display_name, icon_url=song.requester.avatar_url))
        embed.timestamp = datetime.datetime.utcnow()
        return embed


class musicBot(commands.Cog):
    def __init__(self, ctx, bot: commands.Bot):
        self.bot = bot
        self.nowplaying = None
        self.player = music.create_player(ctx, ffmpeg_error_betterfix=True)

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
            await ctx.voice_state.voice.move_to(destination)
            await ctx.send(f'{ctx.author.mention}, connected to: **{destination}**, type **;leave** to leave the channel')
            return
        await destination.connect()
        return await ctx.send(f'{ctx.author.mention}, connected to: **{destination}**, type **;leave** to leave the channel')

    @commands.command(name='leave', aliases=['disconnect'], brief='Makes the bot leave the channel it is in')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _leave(self, ctx):
        """Clears the queue and leaves the voice channel"""
        # await ctx.message.delete()
        try:
            channel = ctx.author.voice.channel
        except:
            return await ctx.send(f'{ctx.author.mention}, join the voice channel that Kookies is in!')
        vc = ctx.voice_client
        if not vc or not vc.is_connected:
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')
        await ctx.voice_client.disconnect()
        return await ctx.send('Left **' + str(channel) + '**')

    @commands.command()
    async def play(self, ctx, *, url):
        player = music.get_player(guild_id=ctx.guild.id)
        if not player:
            player = music.create_player(ctx, ffmpeg_error_betterfix=True)
        if not ctx.voice_client.is_playing():
            await player.queue(url, search=True)
            song = await player.play()
            self.nowplaying = songclass(song, ctx, ctx.author)
            await ctx.send(f"Playing {song.name}")
        else:
            song = await player.queue(url, search=True)
            await ctx.send(f"Queued {song.name}")

    @commands.command(name='pause', aliases=['pau'], brief='Pauses the song playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _pause(self, ctx):
        """Pauses the currently playing song"""
        # await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send(f'{ctx.author.mention}, I am not currently playing anything!')

        else:
            player = music.get_player(guild_id=ctx.guild.id)
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
        player = music.get_player(guild_id=ctx.guild.id)
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

        player = music.get_player(guild_id=ctx.guild.id)
        return await player.stop()

    @commands.command()
    async def loop(self, ctx):
        try:
            player = music.get_player(guild_id=ctx.guild.id)
            song = await player.toggle_song_loop()
        except:
            return await ctx.send(f'{ctx.author.mention}, I am not currently playing anything')
        return await ctx.send(f'{ctx.author.mention}, song loop is now turned ' + ('**on**' if song.is_looping else '**off**'))

    @commands.command()
    async def queue(self, ctx):
        player = music.get_player(guild_id=ctx.guild.id)
        await ctx.send(f"{', '.join([song.name for song in player.current_queue()])}")

    @commands.command(name='now', aliases=['current', 'playing', 'np'], brief='Shows the song that is playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _now(self, ctx):
        # await ctx.message.delete()
        vc = ctx.voice_client
        if not vc:
            return await ctx.send('I am not currently playing anything')
        player = music.get_player(guild_id=ctx.guild.id)
        song = player.now_playing()
        embed = songclass.create_embed(song)
        return await ctx.send(embed=embed)

    @commands.command(name='skip', brief='Skips the song playing')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _skip(self, ctx):
        # await ctx.message.delete()
        vc = ctx.voice_client
        player = music.get_player(guild_id=ctx.guild.id)
        if not vc or not vc.is_connected:
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')

        else:
            data = await player.skip(force=True)
            if len(data) == 2:
                return await ctx.send(f"Skipped from {data[0].name} to {data[1].name}")
            else:
                return await ctx.send(f'{ctx.author.mention} has skipped the song!')

    @commands.command(name='volume', aliases=['vol', 'v'], brief='Set the volume of the music')
    async def _volume(self, ctx, *, volume: int = None):
        """Sets the volume of the player"""
        player = music.get_player(guild_id=ctx.guild.id)
        if volume == None:
            try:
                return await ctx.send(f'{ctx.author.mention}, current volume is at **{ctx.voice_client.source.volume*100}**%')
            except:
                return await ctx.send(f'{ctx.author.mention}, current volume is at **{ctx.voice_state.volume*100}**%')
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel')

        if 0 > volume or volume > 100:
            return await ctx.send(f'{ctx.author.mention}, vvolume must be between 0 and 100')
        song, volume = await player.change_volume(float(volume / 100))
        return await ctx.send(f'{ctx.author.mention} has set the volume to **{volume}**%')

    @commands.command(name='remove', brief='Removes a song from a queue')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _remove(self, ctx, index: int):
        """Removes a song from the queue at a given index"""
        vc = ctx.voice_client
        player = music.get_player(guild_id=ctx.guild.id)
        await player.remove_from_queue(int(index))
        if not vc or not vc.is_connected:
            return await ctx.send(f'{ctx.author.mention}, I am not currently in a voice channel!')
        if len(player.current_queue()) == 0:
            return await ctx.send(f'{ctx.author.mention}, queue is empty')
        elif index > len(player.current_queue()):
            return await ctx.send(f'{ctx.author.mention}, invalid index, number too large')
        else:
            player = music.get_player(guild_id=ctx.guild.id)
            await player.remove_from_queue(int(index))
            return await ctx.send(f'{ctx.author.mention}, removed song number **' + str(index) + '**')


def setup(bot):
    bot.add_cog(musicBot(bot))
