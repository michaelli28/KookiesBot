import discord
import random
import youtube_dl
from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
import shutil
import os
from discord.utils import get
import json
import asyncio
from os import system
import spotdl
import urllib.parse
import urllib.request
import re
from discord import Embed, File, DMChannel
from googleapiclient.discovery import build


client = commands.Bot(command_prefix=';', caseInsensitive=True)

api_key = os.getenv("YOUTUBE_API_KEY")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif str(message.author.id) == 'Magic#6325':
        await message.channel.purge(limit=1)
    await client.process_commands(message)

@client.event
async def on_ready():
    client.load_extension('cogs.Help')
    print('Kookies is ready for Kookie-ing')


@client.event
async def on_member_join(member):
    channel = client.get_channel(668863931200307248)
    await channel.send(member.mention + " has entered!")


@client.event
async def on_member_remove(member):
    channel = client.get_channel(668863931200307248)
    await channel.send(member.name + " has decided we aren't good enough rip")


@client.command()
async def hello(ctx):
    await ctx.send("Hello " + ctx.message.author.mention)


@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    if len(question) == 0:
        ctx.send("Ask a question sir or ma\'am")
    responses = ['Maybe', 'Hmm, try again later', 'Yes sir', 'No sir', 'Yes ma\'am', 'No ma\'am', 'You can count on it!', 'Guarenteed','How did you know?', 'Of course', 'I believe so', 'Nope', 'Definitely NOT', 'Very much so', 'The answer is NO', 'No (u)']
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')


@client.command()
async def klear(ctx, amount=1):
    if amount == 0:
        ctx.send("You need to delete more than 1 message")
    await ctx.channel.purge(limit=amount)
'''
@client.command()
async def join(ctx):
    global voice
    try:
        channel = ctx.message.author.voice.channel
    except:
        await ctx.send('Error: Maybe try to join a voice channel?')
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice is not None:
        return await voice.move_to(channel)
    await channel.connect()
    print(f'The bot has connected to {channel}\n')
    await ctx.send(f'Joined {channel}')
'''

@client.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f'The bot has left {channel}')
        await ctx.send(f'Left {channel}')
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("I'm not in a voice channel")

queueName = []
@client.command()
async def play(ctx, *url: str):
    youtube = build('youtube', 'v3', developerKey=api_key)
    req = youtube.search().list(part='snippet',
                                q=url,
                                type='video',
                                maxResults=1)
    res = req.execute()
    results = re.findall("'title': '(.*?)'", str(res))
    for result in results:
        result = re.sub('&#39;','\'',result)
        result = re.sub('&quot;','\"',result)
    global voice
    global playR
    playR = results[0]
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    try:
        if voice is not None:
            return await voice.move_to(channel)
        await channel.connect()
        print(f'The bot has connected to {channel}\n')
        await ctx.send(f'Joined {channel}')
    except:
        pass

    if len(url) == 0:
        return await ctx.send("Pick a song please")

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1

            try:
                first_file = os.listdir(DIR)[0]

            except:
                print("No more queued song(s)\n")
                queues.clear()
                return

            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(
                os.path.realpath("Queue") + "\\" + first_file)

            if length != 0:
                queueName.pop(0)
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")

                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)

                for file in os.listdir("./"):

                    if file.endswith(".mp3"):
                        
                        os.rename(file, 'song.mp3')
                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.05

            else:
                queues.clear()
                return
        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")
            
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("Error: Music is playing")
        return

    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print('Removed old Queue Folder')
            shutil.rmtree(Queue_folder)

    except:
        print('No old Queue folder')

    await ctx.send("Getting everything ready")

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        "format": 'bestaudio/best',
        'quiet': False,
        'outtmpl': "./song.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    song_search = " ".join(url)
    try:

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([f"ytsearch1:{song_search}"])
            
    except:
        print("Fallback: youtube-dl does not support this URL, using Spotify, this is normal if spotify URL")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -ff song -f " + '"' +
                c_path + '"' + " -s " + song_search)



    voice.play(discord.FFmpegPCMAudio("song.mp3"),
                after=lambda e: check_queue())    
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.05
    await ctx.send('Playing: '+ playR)

@client.command()
async def pause(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing failed to pause")
        await ctx.send("Music not playing, failed to pause")


@client.command()
async def resume(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Music resumed")
        voice.resume()
        await ctx.send("Music resumed")
    else:
        print("Music not paused failed to resume")
        await ctx.send("Music not paused, failed to resume")


@client.command()
async def stop(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    queues.clear()
    queue_infile = os.path.isdir("./Queue")
    if queue_infile is True:
        shutil.rmtree("./Queue")

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")
    else:
        print("No music playing failed to stop")
        await ctx.send("No music playing, failed to stop")

queues = {}


@client.command()
async def queue(ctx, *url: str):
    if url == 0:
        return await ctx.send('Type a song name after q or queue please')
    youtube = build('youtube', 'v3', developerKey=api_key)
    req = youtube.search().list(part='snippet',
                                q=url,
                                type='video',
                                maxResults=1)
    res = req.execute()
    results = re.findall("'title': '(.*?)'", str(res))
    for result in results:
        result = re.sub('&#39;', '\'', result)
        result = re.sub('&quot;', '\"', result)
    queueName.append(results[0])

    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(
        os.path.realpath("Queue") + f'\song{q_num}%(ext)s')

    ydl_opts = {
        "format": 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    song_search = " ".join(url)
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([f"ytsearch1:{song_search}"])
            
    except:
        print("Fallback: youtube-dl does not support this URL, using Spotify, this is normal if spotify URL")
        q_path = os.path.abspath(os.path.realpath("Queue"))
        system(f"spotdl -ff song{q_num} -f " + '"' +
        q_path + '"' + " -s " + song_search)

    await ctx.send("Adding song " + str(q_num) + " to the queue")
    print("Added song to queue\n")


@client.command()
async def skip(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing() and len(queues) != 0:
        print("Playing next song")
        voice.stop()
        await ctx.send("Next song")
    else:
        print("No music playing failed to play next song")
        await ctx.send("No music playing and or no queued songs, failed to skip")


@client.command()
async def volume(ctx, volume: int):
    if volume > 30:
        return await ctx.send("Volume exceeds 30 percent, safety implemented to reduce hearing loss")
    if ctx.voice_client is None:
        return await ctx.send("Not connected to voice channel")

    print(volume/100)

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Changed volume to {volume}%")


@client.command()
async def search(ctx, *url):
    youtube = build('youtube', 'v3', developerKey=api_key)
    req = youtube.search().list(part='snippet',
    q=url,
    type='video',
    maxResults=10)
    res = req.execute()
    results = re.findall("'title': '(.*?)'",str(res))
    embed = discord.Embed(
        color = 0x60c5e6
    )
    embed.set_author(name='Search results')
    i=1
    for result in results:
        resultE = re.sub('&#39;','\'',result)
        resultE = re.sub('&quot;','\"',result)
        embed.add_field(name=str(i)+')',value=(resultE), inline=False)
        i+=1
    await ctx.send('Respond with the number you would like to play', embed=embed)
    msg = await client.wait_for('message', check=lambda message: message.author == ctx.author)
    x=0
    while x != 1:

        if msg.content.lower() == 'stop':
            return await ctx.send('Stopping')
        else:
                global playR 
                playR = results[int(msg.content)-int(1)]
                x = 1
                
    url = playR
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice is not None:
        return await voice.move_to(channel)
    await channel.connect()
    print(f'The bot has connected to {channel}\n')
    await ctx.send(f'Joined {channel}')

    if len(url) == 0:
        return await ctx.send("Pick a song please")

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1

            try:
                first_file = os.listdir(DIR)[0]

            except:
                print("No more queued song(s)\n")
                queues.clear()
                return

            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(
                os.path.realpath("Queue") + "\\" + first_file)

            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")

                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)

                for file in os.listdir("./"):

                    if file.endswith(".mp3"):

                        os.rename(file, 'song.mp3')
                voice.play(discord.FFmpegPCMAudio("song.mp3"),
                    after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.05

            else:
                queues.clear()
                return
        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("Error: Music is playing")
        return

    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print('Removed old Queue Folder')
            shutil.rmtree(Queue_folder)

    except:
        print('No old Queue folder')

    await ctx.send("Getting everything ready")

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        "format": 'bestaudio/best',
        'quiet': False,
        'outtmpl': "./song.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            
        }],
    }

    try:

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([f"ytsearch1:{url}"])

    except:
        print("Fallback: youtube-dl does not support this URL, using Spotify, this is normal if spotify URL")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -ff song -f " + '"' +
                c_path + '"' + " -s " + url)
    
    voice.play(discord.FFmpegPCMAudio("song.mp3"),
                after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.05
    await ctx.send('Playing: ' + playR)
    


@client.command()
async def news(ctx, *, search):
    num_query = search.split(',', 1)
    number_of_results = num_query[0]

    try:
        searchq = num_query[1]
    except:
        number_of_results = 1
        searchq = num_query

    query_string1 = urllib.parse.urlencode({'q': searchq})
    query_string1 = query_string1.encode('utf-8')

    req1=urllib.request.Request(
        'https://news.google.com/', query_string1,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )

    resp1 = urllib.request.urlopen(req1)
    respData1 = resp1.read()

    search_results1 = re.findall('"https://www\.cnn\.com/(.*?)"', str(respData1))
    results = {}
    for n in range(int(number_of_results)):
        results[n+1] = ('https://www.cnn.com/search?' + search_results1[n])
    await ctx.send(results)

@client.command()
async def check(ctx):
    embed = discord.Embed(
        color = 0x60c5e6
    )
    embed.set_author(name='Music Queue')
    if len(queueName)==0:
        if playR == None:
            return await ctx.send('No songs playing or queued')
        else:
            return await ctx.send('Playing: ' + playR)
    
    for i in range(len(queueName)):
        print(queueName)
        embed.add_field(name=str(1)+')',value = queueName[i], inline=False)
    try:
        await ctx.send('Playing: ' + playR, embed=embed)
    except:
        await ctx.send('No music playing')


@client.event
async def on_disconnect():
	print("Bot disconnected")

client.run(os.getenv("DISCORD_TOKEN"))


