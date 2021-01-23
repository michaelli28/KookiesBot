import markovify
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.utils import get
from discord import Embed
from typing import Optional, Union
import json
import discord
from discord.ext import commands
import datetime
import pymongo
from pymongo import MongoClient
import random
import re
import time
from collections import Counter
import asyncio
from discord.ext import tasks
from pytz import timezone
from discord.ext.commands.errors import BadArgument



with open('config.json', 'r') as config:
        configfile = json.load(config)
        config.close()
cooldown = int(configfile['cooldown'])
times = int(configfile['numberoftimes'])

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['sm'], brief='Server mute everyone in a voice channel')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_guild_permissions(mute_members=True)
    async def servermute(self, ctx):
        async with ctx.typing():
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
            for member in channel.members:
                await member.edit(mute=True)
            return await ctx.send('Everyone has been muted')

    @commands.command(aliases=['su'], brief='Unmutes everyone in a voice channel')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_guild_permissions(mute_members=True)
    async def serverunmute(self, ctx):
        async with ctx.typing():
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
            for member in channel.members:
                await member.edit(mute=False)
            return await ctx.send('Everyone has been unmuted')

    @commands.command(aliases=['sd'], brief='Server deafen everyone in a voice channel')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_guild_permissions(deafen_members=True)
    async def serverdeafen(self, ctx):
        async with ctx.typing():
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
            for member in channel.members:
                await member.edit(deafen=True)
            return await ctx.send('Everyone has been deafened')

    @commands.command(aliases=['sud'], brief='Undeafens everyone in a voice channel')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_guild_permissions(deafen_members=True)
    async def serverundeafen(self, ctx):
        async with ctx.typing():
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
            for member in channel.members:
                await member.edit(deafen=False)
            return await ctx.send('Everyone has been undeafened')

    @commands.command(aliases=['n'], brief='Changes someone\'s nickname')
    @commands.has_permissions(manage_nicknames=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def nick(self, ctx, member: discord.Member, *, nick):
        # try:
        old = member.display_name
        await member.edit(nick=nick)
        return await ctx.send(f'Nickname was changed for {member.mention} from {old} to {nick}')
        # except discord.errors.HTTPException:
        #     return await ctx.send('Nickname must be 32 or fewer characters in length')

    @commands.command(brief='Locks the server from messages')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def serverlock(self, ctx):
        try:
            role = ctx.guild.default_role
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, send_messages=False)
            return await ctx.send('Locked the server')
        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')

    @commands.command(brief='Unlocks the server')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def serverunlock(self, ctx):
        try:
            role = ctx.guild.default_role
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, send_messages=None)
            return await ctx.send('Unlocked the server')
        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')

    @commands.command(brief='Locks the channel from messages')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def channellock(self, ctx):
        try:
            channel = ctx.message.channel
            role = ctx.guild.default_role
            await channel.set_permissions(role, send_messages=False)
            return await ctx.send('Locked the channel')
        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')

    @commands.command(brief='Unlocks the channel')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def channelunlock(self, ctx):
        try:
            channel = ctx.message.channel
            role = ctx.guild.default_role
            await channel.set_permissions(role, send_messages=None)
            return await ctx.send('Unlocked the channel')
        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')



    @commands.command(brief='Clears messages')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def klear(self, ctx, amount=1):
        if amount == 0:
            ctx.send("You need to delete a message")
        try:
            await ctx.channel.purge(limit=amount+1)
        except:
            await ctx.send("Input a number please")


    
    @commands.Cog.listener()
    async def on_message(self, message):
        try: #3rd one is my guild
            if str(message.channel.id) == '764120247875272734' or str(message.channel.id) == '751140561255268423' or str(message.guild.id) == '765941083254947911':
                return
        except AttributeError:
            pass
        # if message:
        #     if message.author != self.bot.user:
        #         if message.guild.id == 751137949420224642: #my guild
        #             if message.channel.id != 763009310380654593 and message.channel.id != 761562127617359912: #league channel and r
        #                 if message.author.id != 587068610237693963: #me
        #                     if 'weary' in message.content or 'moan' in message.content or '😩' in message.content:
        #                         await message.delete()
        #                         await message.channel.send(f'{message.author.mention}, That word/emoji has been banned')

        now = datetime.datetime.utcnow()
        current_time = now.strftime("%H:%M|%m/%d/%Y")
        if message.author.id != self.bot.user.id:
            print(
                f"{message.guild}/{message.channel}/  {current_time}  /{message.author.name}>{message.content}  ")
            if message.embeds:
                for embed in message.embeds:
                    print(embed.to_dict())

    @commands.command(aliases=['m'], brief='Mutes someone, need manage roles, if you want to mute one person, ;mute @me [optional time] or if you want to mute everyone, ;mute everyone')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, user: Union[discord.Member, str]=None, minutes: Optional[int]=0):
        
        if user == 'everyone':
            async with ctx.typing():
                try:
                    Muted = get(ctx.message.guild.roles, name='Muted')
                    create = False
                except AttributeError:
                    try:
                        Muted = await ctx.guild.create_role(name="Muted", hoist = True)
                        for channel in ctx.guild.channels:  # removes permission to view and send in the channels
                            await channel.set_permissions(Muted, send_messages=False,
                                                        read_message_history=False,
                                                        read_messages=False)
                        create = True
                    except discord.Forbidden:
                        return await ctx.send('I\'m not allowed to do that')
                for person in ctx.message.guild.members:
                    u = ctx.guild.get_member(person.id)
                    await u.add_roles(Muted)
                if minutes>0:
                    if create:
                        await ctx.send(f'Created muted role, everyone has been muted from chat and will be unmuted in {minutes} minute(s))')
                    else:
                        await ctx.send(f'Everyone has been muted from chat and will be unmuted in {minutes} minute(s))')
                    await asyncio.sleep(int(minutes*60))
                    await user.remove_roles(Muted)
                    return await ctx.send(f'Unmuted everyone after {minutes} minute(s)')
                else:
                    if create:
                        return await ctx.send(f'Created Muted role, muted everyone, no timer')
                    else:
                        return await ctx.send('Muted everyone, no timer')
        if isinstance(user, str):
            return await ctx.send('Invalid user, use everyone to mute everyone')

        else:
            if user == None:
                return await ctx.send('Input a user to mute or everyone')
            try:
                role = get(user.guild.roles, name='Muted')
                create = False

            except discord.Forbidden:
                return await ctx.send('I\'m not allowed to do that')
            except AttributeError:
                Muted = await ctx.guild.create_role(name="Muted", hoist = True)
                for channel in ctx.guild.channels:  # removes permission to view and send in the channels
                    await channel.set_permissions(Muted, send_messages=False,
                                                read_message_history=False,
                                                read_messages=False)
                role = get(user.guild.roles, name='Muted')
                create = True
            if role in user.roles:
                return await ctx.send(f'{user.name} is already muted')
                
            list=[]
            for r in user.roles:
                try:
                    if r.name == '@everyone':
                        pass
                    else:
                        await user.remove_roles(r)
                        list.append(r.name)
                except:
                    if r.name == '@everyone':
                        pass
                    else:
                        await ctx.send(f'Unable to remove role `{r.name}`')

            await user.add_roles(role)
            cluster = MongoClient(
                    'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/Other?retryWrites=true&w=majority')
            db = cluster.Other
            collection = db['Muted']
            id = str(ctx.guild.id)
            id += str(user.id)

            roles = {'_id':id, 'roles':list,'self':False}

            try:
                collection.delete_many({'_id':id})
            except Exception as e:
                print(e)
            collection.insert_one(roles)

            # with open('muted.json', 'r') as file:
            #     stuff = json.load(file)
            #     stuff['ids'].append(roles)
            #     file.close()
            # with open('muted.json', 'w') as file:
            #     json.dump(stuff, file)
            #     file.close()
            
            if minutes>0:
                if create:
                    await ctx.send(f'Created Muted role, `{user.display_name}` has been muted from chat and will be unmuted in {minutes} minute(s))')
                else:
                    await ctx.send(f'`{user.display_name}` has been muted from chat and will be unmuted in {minutes} minute(s))')
                await asyncio.sleep(int(minutes*60))
                await user.remove_roles(role)
                return await ctx.send(f'Unmuted {user.mention} after {minutes} minute(s)')
            else:
                if create:
                    return await ctx.send(f'Created Muted role `{user.display_name}` has been muted from chat (no timer)')
                else:
                    return await ctx.send(f'`{user.display_name}` has been muted from chat (no timer)')


    @commands.command(aliases=['um'], brief='Unmutes someone, need manage roles, set user as everyone to unmute everyone')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, *, user: Union[discord.Member, str]):
        if user == 'everyone':
            async with ctx.typing():
                try:
                    r = get(ctx.message.guild.roles, name='Muted')
                    for person in ctx.message.guild.members:
                        u = ctx.guild.get_member(person.id)
                        await u.remove_roles(r)
                    return await ctx.send(f'Unmuted everyone')

                except discord.Forbidden:
                    return await ctx.send('I\'m not allowed to do that')
                    
        if isinstance(user, str):
            return await ctx.send('Invalid user')
        try:
            role = get(user.guild.roles, name='Muted')

            await user.remove_roles(role)
            # with open('muted.json', 'r') as file:
            #     stuff = json.load(file)
            #     file.close()

            # rolesd = None
            # for dict in stuff['ids']:
            #     if dict['id'] == user.id:
            #         rolesd = dict
            cluster = MongoClient(
                    'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/Other?retryWrites=true&w=majority')
            db = cluster.Other
            collection = db['Muted']
            id = str(ctx.guild.id)
            id += str(user.id)

            result = collection.find_one({'_id':id})
            try:
                roles = result['roles']
            except:
                return await ctx.send(f'Unmuted {user.mention}')

            for role in roles:
                try:
                    if role == '@everyone':
                        pass
                    else:
                        role = get(ctx.message.guild.roles, name=role)
                        await user.add_roles(role)
                except:
                    await ctx.send(f'Unable to add role `{role.name}`')

                # with open('muted.json', 'r') as file:
                #     stuff = json.load(file)
                #     stuff['ids'].remove(rolesd)
                #     file.close()

                # with open('muted.json', 'w') as file:
                #     json.dump(stuff, file)
                #     file.close()
                cluster = MongoClient(
                        'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/Other?retryWrites=true&w=majority')
                db = cluster.Other

                try:
                    collection.delete_many({'_id':id})
                except Exception as e:
                    print(e)
                
            return await ctx.send(f'{user.display_name} has been unmuted')

        except BadArgument:
            return await ctx.send(f'`{user.display_name}` user not found')
        except discord.Forbidden:
            return await ctx.send('I\'m not allowed to do that')
        except AttributeError:
            return await ctx.send('Either `Muted` is not a role, in which case you can use ;mute member to create the muted role, or the member you put was invalid')

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        print('START OF DELETED MESSAGES')
        print('##############################################################################################################################################################')
        for message in messages:
            print(f'{message.guild}/{message.channel}/{message.author}>{message.content}')
            if message.embeds:
                print(message.embeds[0].to_dict())
        print('END OF DELETED MESSAGES')
        print('##############################################################################################################################################################')


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        print('DELETED MESSAGE START')
        print('##############################################################################################################################################################')
        print(f'{message.guild}/{message.channel}/{message.author}>{message.content}')
        if message.embeds:
            print(message.embeds[0].to_dict())
        print('DELETED MESSAGE END')
        print('##############################################################################################################################################################')

    @commands.command(aliases=['ba'], brief='Adds someone to a blacklist so they can\'t use commands')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def blacklistadd(self, ctx, *, member: discord.Member=None):
        if member==None:
            return await ctx.send('Input a member to add to blacklist')
        else:
            with open('blacklist.json', 'r') as blacklist:
                people = json.load(blacklist)
                id = str(member.id) + ' ' + str(ctx.guild.id)
                if id in people['list']:
                    return await ctx.send(f'Member already in blacklist in {ctx.guild.name}')
                else:
                    people['list'].append(id)
                blacklist.close()

            with open('blacklist.json', 'w') as blacklist:
                json.dump(people, blacklist)
                blacklist.close()
        return await ctx.send(f'{member.display_name} has been added to the blacklist in {ctx.guild.name}')

    @commands.command(aliases=['br'], brief='Removes someone to a blacklist so they can use commands again')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def blacklistremove(self, ctx, *, member: discord.Member = None):
        if member == None:
            return await ctx.send('Input a member to remove from blacklist')
        else:
            with open('blacklist.json', 'r') as blacklist:
                people = json.load(blacklist)
                id = str(member.id) + ' ' + str(ctx.guild.id)
                if id not in people['list']:
                    return await ctx.send(f'Member not in blacklist in {ctx.guild.name}')
                else:
                    people['list'].remove(id)
                blacklist.close()

            with open('blacklist.json', 'w') as blacklist:
                json.dump(people, blacklist)
                blacklist.close()
        return await ctx.send(f'{member.display_name} has been removed from the blacklist in {ctx.guild.name}')

    @commands.command(aliases=['bls'], brief='Shows the people in the blacklist')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def blacklistshow(self, ctx):
        with open('blacklist.json', 'r') as blacklist:
            people = json.load(blacklist)
            blacklist.close()
        
        if len(people['list']) == 0:
            return await ctx.send('No blacklisted people!')

        embed = discord.Embed(title=f'Blacklisted People in {ctx.guild.name}', color = random.randint(0, 0xffffff))
        embed.set_author(name=ctx.author.display_name,
                        icon_url=ctx.author.avatar_url)

        embed.timestamp = datetime.datetime.utcnow()

        n=1
        for id in people['list']:
            guildid = id.split()[1]
            if int(guildid) == ctx.guild.id: 
                memberid = id.split()[0]
                member = self.bot.get_user(int(memberid))
                embed.add_field(name=f'{n})', value = f'{member.name}', inline=False)
                n+=1
        return await ctx.send(embed=embed)
                
    @commands.command(aliases=["slowm"], brief="Custom Slow Mode")
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, slowmode: int):
        if slowmode > 21600:
            await ctx.send("Slow Mode too long")
        else:
            await ctx.channel.edit(slowmode_delay=slowmode)
            return await ctx.send(
                f"Slow Mode set to {slowmode} second(s) for {ctx.channel.mention}")

    @commands.command(brief="See your or other peoples permissions", aliases=["permissions"])
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def perms(self, ctx, member: discord.Member = None, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        member = member or ctx.author
        perms = []
        permstr = ""
        for i in member.permissions_in(channel):
            perms.append(i)
        perms = dict(perms)
        for i in perms:
            if perms[i]:
                permstr += (f"✅ {i.replace('_', ' ').title()}\n")

                
        embed = discord.Embed(
            title=f"{member.display_name}'s Permissions", description=permstr, color=0x2F3136
        )
        embed.set_author(name=ctx.author.display_name,
                            icon_url=ctx.author.avatar_url)

        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)

    @commands.command(brief="Blocks a user from chatting in current channel")
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def block(self, ctx, *, user: discord.Member):
        try:
            await ctx.channel.set_permissions(
                user, send_messages=False
            )
            return await ctx.send(f"Blocked {user.mention} from sending messages in **{ctx.channel.name}**")
        except discord.Forbidden:
            return await ctx.send("I don\'t have permissions to do that")

    @commands.command(brief="Unblocks a user from current channel")
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def unblock(self, ctx, *, user: discord.Member):
        try:
            await ctx.channel.set_permissions(
                user, send_messages=None
            )
            return await ctx.send(f"Unblocked {user.mention} from sending messages in **{ctx.channel.name}**")
        except discord.Forbidden:
            return await ctx.send("I don\'t have permissions to do that")


    @commands.command(
        name="clear",
        aliases=["delete", "erase", "purge"],
        brief="Clears a certain amount of messages"
    )
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def clear(self, ctx, amount: int, *, member: discord.Member = None):
        def check(message):
            return message.author.id == member.id

        if not member:
            await ctx.message.delete()
            deleted = await ctx.channel.purge(limit=(amount))
            # a = "message" if len(deleted) else "messages"
            authors = Counter(msg.author.display_name for msg in deleted)
            # message = 
            deleted = sum(authors.values())
            messages = [
                f'**{deleted}** message{" was" if deleted == 1 else "s were"} removed'
            ]
            if deleted:
                authors = sorted(authors.items(), key=lambda t: t[1], reverse=True)
                messages.extend(
                    f"- {count} by **{author}**" for author, count in authors
                )
            await ctx.send("\n".join(messages))
            
        else:
            await ctx.message.delete()
            deleted = await ctx.channel.purge(
                limit=amount,
                check=check,

            )
            return await ctx.send(
                f"Deleted **{len(deleted)}** messages by **{member}**", delete_after=10
            )


    @commands.command(brief="Bans a user")
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def ban(self, ctx, *, member: discord.Member):
        await member.ban()
        return await ctx.send(f"Banned {member.mention} {str(ctx.author)}")


    @commands.command(brief="Bans yourself", aliases=['selfban'])
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def banme(self, ctx):

        await ctx.send('Would you like to ban yourself? Y for yes, N for no')
        def check(m):
            return m.author.id == ctx.author.id
        try:
            response = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send('Please respond Y or N next time')
        if response.content.lower() == 'y' or response.content.lower() == 'yes':
            await ctx.send(f'Bye have a great time {ctx.author.mention} {str(ctx.author)}')
            return await ctx.author.ban()
        
        else:
            return await ctx.send('Good job you are smart!')


    @commands.command(brief="Kicks yourself", aliases=['selfkick'])
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def kickme(self, ctx):

        await ctx.send('Would you like to kick yourself? Y for yes, N for no')
        def check(m):
            return m.author.id == ctx.author.id
        try:
            response = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send('Please respond Y or N next time')
        if response.content.lower() == 'y' or response.content.lower() == 'yes':
            await ctx.send(f'Bye have a great time {ctx.author.mention} {str(ctx.author)}')
            return await ctx.author.kick()
        
        else:
            return await ctx.send('Good job you are smart!')

    @commands.command(brief="Mutes yourself", aliases=['selfmute'])
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def muteme(self, ctx):
        await ctx.send('Would you like to mute yourself? Y for yes, N for no')
        def check(m):
            return m.author.id == ctx.author.id
        try:
            response = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send('Please respond Y or N next time')
        if response.content.lower() == 'y' or response.content.lower() == 'yes':
            
            muted = get(ctx.guild.roles, name='Muted')
            if muted == None:
                return await ctx.send('Muted isn\'t a role, ask admins to do ;mute testuserhere to create the role')
            if muted in ctx.author.roles:
                return await ctx.send('You are already muted')
            else:
                await ctx.send('Type ;unmuteme to unmute')
                list=[]
                for r in ctx.author.roles:
                    try:
                        if r.name == '@everyone':
                            pass
                        else:
                            await ctx.author.remove_roles(r)
                            list.append(r.name)
                    except:
                        if r.name == '@everyone':
                            pass
                        else:
                            await ctx.send(f'Unable to remove role `{r.name}`')

                await ctx.author.add_roles(muted)
                cluster = MongoClient(
                    'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/Other?retryWrites=true&w=majority')
                db = cluster.Other
                collection = db['Muted']
                id = str(ctx.guild.id)
                id += str(ctx.author.id)

                roles = {'_id':id, 'roles':list,'self':True}

                try:
                    collection.delete_many({'_id':id})
                except Exception as e:
                    print(e)
                collection.insert_one(roles)
                # with open('muted.json', 'r') as file:
                #     stuff = json.load(file)
                #     stuff['ids'].append(roles)
                #     file.close()
                # with open('muted.json', 'w') as file:
                #     json.dump(stuff, file)
                #     file.close()
        else:
            return await ctx.send('Not muting')

    @commands.command(brief="Unmutes yourself", aliases=['selfunmute'])
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def unmuteme(self, ctx):
        async with ctx.typing():
            role = get(ctx.guild.roles, name='Muted')
            if role == None:
                return await ctx.send('Muted isn\'t a role, ask admins to do ;mute testuserhere to create the role')
            else:
                if role not in ctx.author.roles:
                    return await ctx.send('You aren\'t already muted')
                # with open('muted.json', 'r') as file:
                #     stuff = json.load(file)
                #     file.close()
                # selfm = False
                # rolesd = None
                # for dict in stuff['ids']:
                #     if dict['id'] == ctx.author.id:
                #         if dict['self'] == True:
                #             rolesd = dict
                #             selfm = True
                cluster = MongoClient(
                    'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/Other?retryWrites=true&w=majority')
                db = cluster.Other
                collection = db['Muted']
                id = str(ctx.guild.id)
                id += str(ctx.author.id)


                results = collection.find({'_id': id})
                selfmute = None
                doc = None
                for document in results:
                    mute = document['self']
                    if mute == True:
                        if selfmute == None:
                            selfmute = True
                        if doc == None:
                            doc = document
                    elif mute == False:
                        selfmute = False
                        doc = document
                        break
                if selfmute == False:
                    return await ctx.send('You tried to unmute yourself when a mod muted you... it failed (this may be false)')
                
                await ctx.author.remove_roles(role)
                await ctx.send('Unmuting!')
                for role in doc['roles']:
                    try:
                        if role == '@everyone':
                            pass
                        else:
                            role = get(ctx.message.guild.roles, name=role)
                            await ctx.author.add_roles(role)
                    except:
                        await ctx.send(f'Unable to add role `{role.name}`')
                try:
                    collection.delete_many({'_id':id})
                except Exception as e:
                    print(e)
                return 
                # with open('muted.json', 'r') as file:
                #     stuff = json.load(file)
                #     stuff['ids'].remove(rolesd)
                #     file.close()
                # with open('muted.json', 'w') as file:
                #     json.dump(stuff, file)
                #     file.close()

    
    @commands.command(
        brief="Unbans a previously banned user with their name and discriminator"
    )
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member: Union[int, str]):
        if isinstance(member, str):
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split("#")
            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (
                    member_name,
                    member_discriminator,
                ):
                    await ctx.guild.unban(user)
                    return await ctx.send(f"Unbanned {user.mention}")
            await ctx.send("User not found/banned")

        else:
            await ctx.guild.unban(discord.Object(id=member))
            return await ctx.send(f"Unbanned member with id {member}")
    
    @commands.command(brief="Kicks a user", aliases=['cic'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, *, member: discord.Member):
        await member.kick()
        return await ctx.send(f"Kicked {member.mention}")

def setup(bot):
	bot.add_cog(moderation(bot))
