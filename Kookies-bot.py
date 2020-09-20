import discord
import random
import youtube_dl
from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound
import shutil
import os
from discord.utils import get
import json
import asyncio
from os import system
#import spotdl
import urllib.parse
import urllib.request
import re
from discord import Embed, File, DMChannel
# from googleapiclient.discovery import build
import time
from time import time
global PREFIX
PREFIX=';'
bot = commands.Bot(command_prefix=PREFIX, caseInsensitive=True, description='Kookies FOR THE WIN')



@bot.event
async def on_ready():
    bot.load_extension('cogs.Help')
    #bot.load_extension('cogs.Music2')
    bot.load_extension('cogs.CommandErrorHandler')
    bot.load_extension('cogs.Leaderboard')
    bot.load_extension('cogs.MusicPlayer')
    bot.load_extension('cogs.Level-Schoology')

    print('Logged in as:\n{0.user.name}'.format(bot))



#allows server members to set channel for welcome messages to send to
@bot.command(brief='Sets the channel for welcome messages')
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.is_owner()
async def welcome(ctx):
    with open("guild.json", "r") as f:
        guildInfo = json.load(f)
# sets channel to send message to as the channel the command was sent to
    guildInfo[ctx.message.guild.id]=ctx.message.channel.id

    with open("guild.json", "w") as f:  
        try:
            json.dump(guildInfo, f)
        except:
            pass
    await ctx.send('Channel set to: '+str(ctx.message.channel.id))

@bot.event
async def on_member_join(member):
    # role = discord.utils.get(member.server.roles, name='Member')
    # await client.add_roles(member, role)

    embed = discord.Embed(title='Welcome to '+ str(member.guild.name), color=random.randint(0, 0xffffff))

    embed.set_author(name=member.name, icon_url=member.avatar_url)
    with open("guild.json", "r") as f:
        guildInfo = json.load(f)

    channel = guildInfo[str(member.guild.id)]
    channel = bot.get_channel(channel)
    await channel.send(embed=embed)

# @bot.event
# async def on_member_join(member):
#     channel = bot.get_channel(751137949420224645)
#     await channel.send(member.mention + " has entered!")


@bot.event
async def on_member_remove(member):
    embed = discord.Embed(color=random.randint(0, 0xffffff))
    embed.set_author(name=str(member.name)+' has left '+str(member.guild.name))
    embed.set_author(name=member.name, icon_url=member.avatar_url)
    with open("guild.json", "r") as f:
        guildInfo = json.load(f)

    channel = guildInfo[str(member.guild.id)]
    channel = bot.get_channel(channel)
    await channel.send(embed=embed)

@bot.command(aliases=['ar'], brief='Gives someone a role, need manage roles')
# This must be exactly the name of the appropriate role
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, user: discord.Member, *, role):
    try:
        await user.add_roles(get(user.guild.roles, name=role))
        await ctx.send(f'Gave {user.role} the ' + role)
    except:
        return await ctx.send('That is not a valid role or user')
    

@bot.command(aliases=['m'],brief='Mutes someone, need manage roles')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, user: discord.Member):
    try:
        role = get(user.guild.roles, name='Muted')
        await user.add_roles(role)
        await ctx.send(f'{user.name} has been muted from chat')
    except:
        return await ctx.send('That is not a valid user')

@bot.command(aliases=['rr'], brief='Removes a role, need manage roles')
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, user: discord.Member, *, role):
    try:
        role = get(user.guild.roles, name=role)
        await user.remove_roles(role)
        await ctx.send(f'{role} role was removed from {user.name}')
    except:
        return await ctx.send('That is not a valid role or user')
        
@bot.command(brief='Says hello')
@commands.cooldown(1, 5, commands.BucketType.user)
async def hello(ctx):
    await ctx.send("Hello " + ctx.message.author.mention)

@bot.command(brief='Get your id')
async def id(ctx):
    author = ctx.message.author.id
    await ctx.send(author)
    
@bot.command(aliases=['8ball'], brief='Answer your yes/no questions')
@commands.cooldown(1, 5, commands.BucketType.user)
async def _8ball(ctx, *, question=None):
    if (question) == None:
        return await ctx.send("Ask a question sir or ma\'am")
    responses = ['Maybe', 'Hmm, try again later', 'Yes sir/ma\'am', 'No sir/ma\'am', 'You can count on it!', 'Guaranteed','How did you know?', 'Of course', 'I believe so', 'Nope', 'Definitely NOT', 'Very much so', 'The answer is NO', 'No (u)', 'Does money grow on trees?', 'Is magic better than Kookies? (NOOOO)']
    e = discord.Embed(
        title='8ball response',
        color = random.randint(0, 0xffffff)
    )
    e.add_field(name='Question',value=question, inline=False)
    e.add_field(name='Answer',value=random.choice(responses), inline=False)
    e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=e)

@bot.command(brief='Clears messages, NotThatBot#3360 only')
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.is_owner()
async def klear(ctx, amount=1):
    if amount == 0:
        ctx.send("You need to delete a message")
    try:
        await ctx.channel.purge(limit=amount)
    except:
        await ctx.send("Input a number please")

@bot.command(brief='Gets news from CNN')
@commands.cooldown(1, 5, commands.BucketType.user)
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

@bot.command(brief='Get your ping')
@commands.cooldown(1, 5, commands.BucketType.user)
async def ping(ctx):
    start = time()
    message = await ctx.send(f"Pong! Latency: {bot.latency*1000:,.0f} ms.")
    end = time()

    await message.edit(content=f"Pong! Latency: {bot.latency*1000:,.0f} ms. Response time: {(end-start)*1000:,.0f} ms.")

@bot.event
async def on_message(message):
    if message.author != bot.user:
        if message.content.startswith('no u'):
            return await message.channel.send('no u', delete_after=10)
    if message.author == bot.user:
        await message.add_reaction('❌')
    await bot.process_commands(message)
    #if message.author.id == '740226974248730625':
        #await message.delete()
    #    await message.channel.send('MAGIC SUCKS')
    #if message.content.startswith('-'):
        #await message.delete()
    #    await message.channel.send('MAGIC SUCKS')

@bot.event
async def on_raw_reaction_add(payload):
    channel = discord.utils.get(bot.get_all_channels(), id=payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if payload.emoji.name == '❌':
        if (not payload.member.bot):
            try:
                await message.delete()
            except:
                pass

@bot.command(brief='Kicks people, admin only')
@commands.cooldown(1, 5, commands.BucketType.user)
@has_permissions(administrator=True)
async def cic(ctx, user: discord.Member):
    await user.kick(reason='Admins decided you needed a kick')
    return await ctx.send(str(user) + ' has been kicked')
    #await ctx.send('Missing Permissions to kick ' + str(user))
@bot.command(name='botstop', aliases=['bstop'], brief='Shutdown the bot, NotThatBot#3360 only')
@commands.is_owner()
async def botstop(ctx):
    print('Goodbye')
    await ctx.send('Goodbye')
    await bot.logout()
    return
# @bot.event
# async def on_disconnect():
# 	print("Bot disconnected")

bot.run('NzQzODU5NDIwNzk4MTI0MDQz.XzazEg.H8jmotH113mVSyRdNnU76aZ1P74')



'''@bot.command()
async def join(ctx):
    global voice
    try:
        channel = ctx.message.author.voice.channel
    except:
        await ctx.send('Error: Maybe try to join a voice channel?')
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice is not None:
        return await voice.move_to(channel)
    await channel.connect()
    print(f'The bot has connected to {channel}\n')
    await ctx.send(f'Joined {channel}')


@bot.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f'The bot has left {channel}')
        await ctx.send(f'Left {channel}')
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("I'm not in a voice channel")

queueName = []
@bot.command()
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
        result = re.sub('&amp;','&',result)
    global voice
    global playR
    playR = results[0]
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
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
                voice.source.volume = 0.10

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

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        "format": 'bestaudio/best',
        'quiet': False,
        'outtmpl': "./song.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            'source_address': '0.0.0.0'
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
    voice.source.volume = 0.10
    try:
        await ctx.send('Playing: '+ playR)
    except:
        pass
@bot.command()
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing failed to pause")
        await ctx.send("Music not playing, failed to pause")


@bot.command()
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Music resumed")
        voice.resume()
        await ctx.send("Music resumed")
    else:
        print("Music not paused failed to resume")
        await ctx.send("Music not paused, failed to resume")


@bot.command()
async def stop(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

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


@bot.command()
async def queue(ctx, *url: str):
    if url == 0:
        return await ctx.send('Type a song name after q or queue please')
    if play != 1:
        return await ctx.send('No song playing, try ;play [song name] before queuing a song')
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
        result = re.sub('&amp;','&',result)
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
            'source_address': '0.0.0.0'
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


@bot.command()
async def skip(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing() and len(queues) != 0:
        print("Playing next song")
        voice.stop()
        await ctx.send("Next song")
    else:
        print("No music playing failed to play next song")
        await ctx.send("No music playing and or no queued songs, failed to skip")


@bot.command()
async def volume(ctx, volume: int):
    if volume > 30:
        return await ctx.send("Volume exceeds 30 percent, safety implemented to reduce hearing loss")
    if ctx.voice_client is None:
        return await ctx.send("Not connected to voice channel")

    print(volume/100)

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Changed volume to {volume}%")

@bot.command()
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
        resultE = re.sub('&amp;','&',result)
        embed.add_field(name=str(i)+')',value=(resultE), inline=False)
        i+=1
    await ctx.send('Respond with the number you would like to play', embed=embed)
    msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
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
    voice = get(bot.voice_clients, guild=ctx.guild)

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
                voice.source.volume = 0.10

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

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        "format": 'bestaudio/best',
        'quiet': False,
        'outtmpl': "./song.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            'source_address': '0.0.0.0'
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
    voice.source.volume = 0.10
    await ctx.send('Playing: ' + playR)
    
'''
