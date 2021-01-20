import discord
import random
from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound
from discord.ext.commands.errors import BadArgument
import shutil
import os
from discord.utils import get
import json
import asyncio
from os import system
import youtube_dl
import sys
import datetime
from pytz import timezone
#import spotdl
from typing import Optional
import re
import sys
from discord import Embed, File, DMChannel
import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet
from googleapiclient.discovery import build
import time
from time import time
from aiohttp import ClientSession
import io
import logging
#import jishaku
# from dotenv import load_dotenv
# load_dotenv()


PREFIX = ';'

#Below is blank space for future reference
#᲼᲼᲼᲼᲼᲼#
intents = discord.Intents.all()

async def startup():
    await bot.wait_until_ready()
    activity = discord.Game(name=";help")
    await bot.change_presence(activity=activity)
    # bot.load_extension('cogs.Music2')
    bot.client = ClientSession()
    bot.load_extension('cogs.CommandErrorHandler')
    bot.load_extension('cogs.fun')
    bot.load_extension('cogs.helpmenu')
    bot.load_extension('cogs.levels')
    bot.load_extension('cogs.moderation')
    bot.load_extension('cogs.musiclava')
    bot.load_extension('cogs.roles')
    bot.load_extension('cogs.server')
    bot.load_extension('cogs.misc')
    bot.load_extension('cogs.utility')
    bot.load_extension('cogs.games')
    bot.load_extension('jishaku')
    #bot.load_extension('cogs.school')


bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), case_insensitive=True, intents=intents, owner_id=587068610237693963)
bot.loop.create_task(startup())
# 630499390938808379 hurb id

# youtube_dl.utils.bug_reports_message = lambda: ''
# ydl = youtube_dl.YoutubeDL({"format": "bestaudio/best", "restrictfilenames": True, "noplaylist": True, "nocheckcertificate": True,
#                             "ignoreerrors": True, "logtostderr": False, "quiet": True, "no_warnings": True, "source_address": "0.0.0.0"})
#     data = await bot.loop.run_in_executor(None, lambda: ydl.extract_info('https://www.youtube.com/watch?v=RXLzvo6kvVQ', download=True))

@bot.event
async def on_ready():
    print('Logged in as:\n{0.user.name}'.format(bot))


@bot.check
async def blacklisted(ctx):
    with open('blacklist.json') as thing:
        blacklist = json.load(thing)
        blacklist = blacklist['list']
        thing.close()
    id = str(ctx.author.id) + " " + str(ctx.guild.id)
    if id in blacklist and id.split()[0] != '587068610237693963':
        await ctx.send(f'{ctx.author.mention}, you have been blacklisted from this bot in **{ctx.guild.name}**')
        return False
    else:
        return True

class blacklisterror(commands.CheckFailure):
    pass


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author != bot.user:
        if message.content.startswith('no u'):
            with open('blacklist.json') as thing:
                blacklist = json.load(thing)
                blacklist = blacklist['list']
                thing.close()
            if str(message.author.id) in blacklist and str(message.author.id) != '587068610237693963':
                return await message.channel.send(f'{message.author.mention}, you have been blacklisted from this bot')
            else:
                return await message.channel.send('no u', delete_after=5)
        if message.guild == None:
            return
        if message.content.startswith(';'):
            with open('config.json', 'r') as config:
                info = json.load(config)
                config.close()

            if str(message.guild.id) not in info:
                return
            elif info[str(message.guild.id)]['prune']:
                await asyncio.sleep(int(info[str(message.guild.id)]['time']))
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass
            else:
                return

    elif message.author == bot.user:
        if message.embeds:
            if message.embeds[0].title == 'Role Reactions':
                return
                
        await asyncio.sleep(4)
        try:
            await message.add_reaction('❌')
        except discord.errors.NotFound:
            pass
        with open('config.json', 'r') as config:
            info = json.load(config)
            config.close()
        if message.guild == None:
            return
        elif str(message.guild.id) not in info:
            return
        elif info[str(message.guild.id)]['prune']:
            await asyncio.sleep(int(info[str(message.guild.id)]['time']))
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
        else:
            return


#TOKEN = os.getenv('TOKEN')
bot.run('NzQzODU5NDIwNzk4MTI0MDQz.XzazEg.5eqdaTAYnnNjPy7HEnxemnLgx_c')






# @bot.command()
# async def join(ctx):
#     global voice
#     try:
#         channel = ctx.message.author.voice.channel
#     except:
#         await ctx.send('Error: Maybe try to join a voice channel?')
#     voice = get(bot.voice_clients, guild=ctx.guild)

#     if voice is not None:
#         return await voice.move_to(channel)
#     await channel.connect()
#     print(f'The bot has connected to {channel}\n')
#     await ctx.send(f'Joined {channel}')


# @bot.command()
# async def leave(ctx):
#     channel = ctx.message.author.voice.channel
#     voice = get(bot.voice_clients, guild=ctx.guild)

#     if voice and voice.is_connected():
#         await voice.disconnect()
#         print(f'The bot has left {channel}')
#         await ctx.send(f'Left {channel}')
#     else:
#         print("Bot was told to leave voice channel, but was not in one")
#         await ctx.send("I'm not in a voice channel")

# queueName = []
# @bot.command()
# async def play(ctx, *url: str):
#     youtube = build('youtube', 'v3', developerKey=api_key)
#     req = youtube.search().list(part='snippet',
#                                 q=url,
#                                 type='video',
#                                 maxResults=1)
#     res = req.execute()
#     results = re.findall("'title': '(.*?)'", str(res))
#     for result in results:
#         result = re.sub('&#39;','\'',result)
#         result = re.sub('&quot;','\"',result)
#         result = re.sub('&amp;','&',result)
#     global voice
#     global playR
#     playR = results[0]
#     channel = ctx.message.author.voice.channel
#     voice = get(bot.voice_clients, guild=ctx.guild)
#     try:
#         if voice is not None:
#             return await voice.move_to(channel)
#         await channel.connect()
#         print(f'The bot has connected to {channel}\n')
#         await ctx.send(f'Joined {channel}')
#     except:
#         pass

#     if len(url) == 0:
#         return await ctx.send("Pick a song please")

#     def check_queue():
#         Queue_infile = os.path.isdir("./Queue")
#         if Queue_infile is True:
#             DIR = os.path.abspath(os.path.realpath("Queue"))
#             length = len(os.listdir(DIR))
#             still_q = length - 1

#             try:
#                 first_file = os.listdir(DIR)[0]

#             except:
#                 print("No more queued song(s)\n")
#                 queues.clear()
#                 return

#             main_location = os.path.dirname(os.path.realpath(__file__))
#             song_path = os.path.abspath(
#                 os.path.realpath("Queue") + "\\" + first_file)

#             if length != 0:
#                 queueName.pop(0)
#                 print("Song done, playing next queued\n")
#                 print(f"Songs still in queue: {still_q}")
#                 song_there = os.path.isfile("song.mp3")

#                 if song_there:
#                     os.remove("song.mp3")
#                 shutil.move(song_path, main_location)

#                 for file in os.listdir("./"):

#                     if file.endswith(".mp3"):
                        
#                         os.rename(file, 'song.mp3')
#                 voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
#                 voice.source = discord.PCMVolumeTransformer(voice.source)
#                 voice.source.volume = 0.10

#             else:
#                 queues.clear()
#                 return
#         else:
#             queues.clear()
#             print("No songs were queued before the ending of the last song\n")
#     song_there = os.path.isfile("song.mp3")
#     try:
#         if song_there:
#             os.remove("song.mp3")
#             queues.clear()
#             print("Removed old song file")
#     except PermissionError:
#         print("Trying to delete song file, but it's being played")
#         await ctx.send("Error: Music is playing")
#         return

#     Queue_infile = os.path.isdir("./Queue")
#     try:
#         Queue_folder = "./Queue"
#         if Queue_infile is True:
#             print('Removed old Queue Folder')
#             shutil.rmtree(Queue_folder)

#     except:
#         print('No old Queue folder')

#     await ctx.send("Getting everything ready")

#     voice = get(bot.voice_clients, guild=ctx.guild)

#     ydl_opts = {
#         "format": 'bestaudio/best',
#         'quiet': False,
#         'outtmpl': "./song.mp3",
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#             'source_address': '0.0.0.0'
#         }],
#     }

#     song_search = " ".join(url)
#     try:

#         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#             print("Downloading audio now\n")
#             ydl.download([f"ytsearch1:{song_search}"])
            
#     except:
#         print("Fallback: youtube-dl does not support this URL, using Spotify, this is normal if spotify URL")
#         c_path = os.path.dirname(os.path.realpath(__file__))
#         system("spotdl -ff song -f " + '"' +
#                 c_path + '"' + " -s " + song_search)



#     voice.play(discord.FFmpegPCMAudio("song.mp3"),
#                 after=lambda e: check_queue())    
#     voice.source = discord.PCMVolumeTransformer(voice.source)
#     voice.source.volume = 0.10
#     try:
#         await ctx.send('Playing: '+ playR)
#     except:
#         pass
# @bot.command()
# async def pause(ctx):

#     voice = get(bot.voice_clients, guild=ctx.guild)

#     if voice and voice.is_playing():
#         print("Music paused")
#         voice.pause()
#         await ctx.send("Music paused")
#     else:
#         print("Music not playing failed to pause")
#         await ctx.send("Music not playing, failed to pause")


# @bot.command()
# async def resume(ctx):

#     voice = get(bot.voice_clients, guild=ctx.guild)

#     if voice and voice.is_paused():
#         print("Music resumed")
#         voice.resume()
#         await ctx.send("Music resumed")
#     else:
#         print("Music not paused failed to resume")
#         await ctx.send("Music not paused, failed to resume")


# @bot.command()
# async def stop(ctx):

#     voice = get(bot.voice_clients, guild=ctx.guild)

#     queues.clear()
#     queue_infile = os.path.isdir("./Queue")
#     if queue_infile is True:
#         shutil.rmtree("./Queue")

#     if voice and voice.is_playing():
#         print("Music stopped")
#         voice.stop()
#         await ctx.send("Music stopped")
#     else:
#         print("No music playing failed to stop")
#         await ctx.send("No music playing, failed to stop")

# queues = {}


# @bot.command()
# async def queue(ctx, *url: str):
#     if url == 0:
#         return await ctx.send('Type a song name after q or queue please')
#     if play != 1:
#         return await ctx.send('No song playing, try ;play [song name] before queuing a song')
#     youtube = build('youtube', 'v3', developerKey=api_key)
#     req = youtube.search().list(part='snippet',
#                                 q=url,
#                                 type='video',
#                                 maxResults=1)
#     res = req.execute()
#     results = re.findall("'title': '(.*?)'", str(res))
#     for result in results:
#         result = re.sub('&#39;', '\'', result)
#         result = re.sub('&quot;', '\"', result)
#         result = re.sub('&amp;','&',result)
#     queueName.append(results[0])

#     Queue_infile = os.path.isdir("./Queue")
#     if Queue_infile is False:
#         os.mkdir("Queue")
#     DIR = os.path.abspath(os.path.realpath("Queue"))
#     q_num = len(os.listdir(DIR))
#     q_num += 1
#     add_queue = True
#     while add_queue:
#         if q_num in queues:
#             q_num += 1
#         else:
#             add_queue = False
#             queues[q_num] = q_num

#     queue_path = os.path.abspath(
#         os.path.realpath("Queue") + f'\song{q_num}%(ext)s')

#     ydl_opts = {
#         "format": 'bestaudio/best',
#         'quiet': True,
#         'outtmpl': queue_path,
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#             'source_address': '0.0.0.0'
#         }],
#     }

#     song_search = " ".join(url)
#     try:
#         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#             print("Downloading audio now\n")
#             ydl.download([f"ytsearch1:{song_search}"])
            
#     except:
#         print("Fallback: youtube-dl does not support this URL, using Spotify, this is normal if spotify URL")
#         q_path = os.path.abspath(os.path.realpath("Queue"))
#         system(f"spotdl -ff song{q_num} -f " + '"' +
#         q_path + '"' + " -s " + song_search)

#     await ctx.send("Adding song " + str(q_num) + " to the queue")
#     print("Added song to queue\n")


# @bot.command()
# async def skip(ctx):

#     voice = get(bot.voice_clients, guild=ctx.guild)

#     if voice and voice.is_playing() and len(queues) != 0:
#         print("Playing next song")
#         voice.stop()
#         await ctx.send("Next song")
#     else:
#         print("No music playing failed to play next song")
#         await ctx.send("No music playing and or no queued songs, failed to skip")


# @bot.command()
# async def volume(ctx, volume: int):
#     if volume > 30:
#         return await ctx.send("Volume exceeds 30 percent, safety implemented to reduce hearing loss")
#     if ctx.voice_client is None:
#         return await ctx.send("Not connected to voice channel")

#     print(volume/100)

#     ctx.voice_client.source.volume = volume / 100
#     await ctx.send(f"Changed volume to {volume}%")

# @bot.command()
# async def search(ctx, *url):
#     youtube = build('youtube', 'v3', developerKey=api_key)
#     req = youtube.search().list(part='snippet',
#     q=url,
#     type='video',
#     maxResults=10)
#     res = req.execute()
#     results = re.findall("'title': '(.*?)'",str(res))
#     embed = discord.Embed(
#         color = 0x60c5e6
#     )
#     embed.set_author(name='Search results')
#     i=1
#     for result in results:
#         resultE = re.sub('&#39;','\'',result)
#         resultE = re.sub('&quot;','\"',result)
#         resultE = re.sub('&amp;','&',result)
#         embed.add_field(name=str(i)+')',value=(resultE), inline=False)
#         i+=1
#     await ctx.send('Respond with the number you would like to play', embed=embed)
#     msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
#     x=0
#     while x != 1:

#         if msg.content.lower() == 'stop':
#             return await ctx.send('Stopping')
#         else:
#                 global playR 
#                 playR = results[int(msg.content)-int(1)]
#                 x = 1
                
#     url = playR
#     global voice
#     channel = ctx.message.author.voice.channel
#     voice = get(bot.voice_clients, guild=ctx.guild)

#     if voice is not None:
#         return await voice.move_to(channel)
#     await channel.connect()
#     print(f'The bot has connected to {channel}\n')
#     await ctx.send(f'Joined {channel}')

#     if len(url) == 0:
#         return await ctx.send("Pick a song please")

#     def check_queue():
#         Queue_infile = os.path.isdir("./Queue")
#         if Queue_infile is True:
#             DIR = os.path.abspath(os.path.realpath("Queue"))
#             length = len(os.listdir(DIR))
#             still_q = length - 1

#             try:
#                 first_file = os.listdir(DIR)[0]

#             except:
#                 print("No more queued song(s)\n")
#                 queues.clear()
#                 return

#             main_location = os.path.dirname(os.path.realpath(__file__))
#             song_path = os.path.abspath(
#                 os.path.realpath("Queue") + "\\" + first_file)

#             if length != 0:
#                 print("Song done, playing next queued\n")
#                 print(f"Songs still in queue: {still_q}")
#                 song_there = os.path.isfile("song.mp3")

#                 if song_there:
#                     os.remove("song.mp3")
#                 shutil.move(song_path, main_location)

#                 for file in os.listdir("./"):

#                     if file.endswith(".mp3"):

#                         os.rename(file, 'song.mp3')
#                 voice.play(discord.FFmpegPCMAudio("song.mp3"),
#                     after=lambda e: check_queue())
#                 voice.source = discord.PCMVolumeTransformer(voice.source)
#                 voice.source.volume = 0.10

#             else:
#                 queues.clear()
#                 return
#         else:
#             queues.clear()
#             print("No songs were queued before the ending of the last song\n")

#     song_there = os.path.isfile("song.mp3")
#     try:
#         if song_there:
#             os.remove("song.mp3")
#             queues.clear()
#             print("Removed old song file")
#     except PermissionError:
#         print("Trying to delete song file, but it's being played")
#         await ctx.send("Error: Music is playing")
#         return

#     Queue_infile = os.path.isdir("./Queue")
#     try:
#         Queue_folder = "./Queue"
#         if Queue_infile is True:
#             print('Removed old Queue Folder')
#             shutil.rmtree(Queue_folder)

#     except:
#         print('No old Queue folder')

#     await ctx.send("Getting everything ready")

#     voice = get(bot.voice_clients, guild=ctx.guild)

#     ydl_opts = {
#         "format": 'bestaudio/best',
#         'quiet': False,
#         'outtmpl': "./song.mp3",
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#             'source_address': '0.0.0.0'
#         }],
#     }

#     try:

#         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#             print("Downloading audio now\n")
#             ydl.download([f"ytsearch1:{url}"])

#     except:
#         print("Fallback: youtube-dl does not support this URL, using Spotify, this is normal if spotify URL")
#         c_path = os.path.dirname(os.path.realpath(__file__))
#         system("spotdl -ff song -f " + '"' +
#                 c_path + '"' + " -s " + url)
    
#     voice.play(discord.FFmpegPCMAudio("song.mp3"),
#                 after=lambda e: check_queue())
#     voice.source = discord.PCMVolumeTransformer(voice.source)
#     voice.source.volume = 0.10
#     await ctx.send('Playing: ' + playR)

