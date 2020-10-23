import markovify
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.menus import MenuPages, ListPageSource
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

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['sm'], brief='Server mute everyone in a voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(mute_members=True)
    async def servermute(self, ctx):
        async with ctx.typing():
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
            for member in channel.members:
                await member.edit(mute=True)
            return await ctx.send('Everyone has been muted')

    @commands.command(aliases=['su'], brief='Unmutes everyone in a voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(mute_members=True)
    async def serverunmute(self, ctx):
        async with ctx.typing():
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
            for member in channel.members:
                await member.edit(mute=False)
            return await ctx.send('Everyone has been unmuted')

    @commands.command(aliases=['sd'], brief='Server deafen everyone in a voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(deafen_members=True)
    async def serverdeafen(self, ctx):
        async with ctx.typing():
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
            for member in channel.members:
                await member.edit(deafen=True)
            return await ctx.send('Everyone has been deafened')

    @commands.command(aliases=['sud'], brief='Undeafens everyone in a voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def nick(self, ctx, member: discord.Member, *, nick):
        old = member.display_name
        await member.edit(nick=nick)
        return await ctx.send(f'Nickname was changed for {member.mention} from {old} to {nick}')

    @commands.command(brief='Locks the server from messages')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def channelunlock(self, ctx):
        try:
            channel = ctx.message.channel
            role = ctx.guild.default_role
            await channel.set_permissions(role, send_messages=None)
            return await ctx.send('Unlocked the channel')
        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')

    @commands.command(brief='Creates a channel')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def createchannel(self, ctx, name):
        guild = ctx.message.guild
        await guild.create_text_channel(name)
        return await ctx.send(f'Created text chanenl {name}')

    @commands.command(brief='Creates a voice channel')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def createvoicechannel(self, ctx, name):
        guild = ctx.message.guild
        await guild.create_voice_channel(name)
        return await ctx.send(f'Created voice channel {name}')

    @commands.command(brief='Edits a text channel')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def editchannel(self, ctx, name: discord.TextChannel, nname: Optional[str] = None, slowmode: Optional[int] = None):
        if nname != None:
            await name.edit(name=nname)
            await ctx.send(f'Changed the name of channel {name.name} to {nname}')
        if slowmode != None:
            await name.edit(slowmode_delay=slowmode)
            return await ctx.send(f'Set the slowmode delay for channel {name.name} to {slowmode} seconds')

    @commands.command(brief='Creates a category')
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def createcategory(self, ctx, name):
        guild = ctx.message.guild
        await guild.create_category(name)
        return await ctx.send(f'Created category {name}')

    @commands.command(brief='Clears messages')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def klear(self, ctx, amount=1):
        if amount == 0:
            ctx.send("You need to delete a message")
        try:
            await ctx.channel.purge(limit=amount+1)
        except:
            await ctx.send("Input a number please")


    # allows server members to set channel for welcome messages to send to
    @commands.command(brief='Sets the channel for welcome messages')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx):
        with open("guild.json", "r") as f:
            guildInfo = json.load(f)
            f.close()
    # sets channel to send message to as the channel the command was sent to
        guildInfo[ctx.message.guild.id] = ctx.message.channel.id

        with open("guild.json", "w") as f:
            try:
                json.dump(guildInfo, f)
            except:
                pass
            f.close()
        return await ctx.send('Channel set to: '+str(ctx.message.channel.id))


    @commands.Cog.listener()
    async def on_member_join(self, member):
        # role = discord.utils.get(member.server.roles, name='Member')
        # await client.add_roles(member, role)
        # if str(member.name) == 'zero0two2':
        #     Muted = get(member.guild.roles, name='Muted')
        #     u = member.guild.get_member(member.id)
        #     await u.add_roles(Muted)
        embed = discord.Embed(
            title='Welcome to ' + str(member.guild.name) + " " + str(member.display_name), color=random.randint(0, 0xffffff))

        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()

        with open("guild.json", "r") as f:
            guildInfo = json.load(f)
            f.close()
        channel = guildInfo[str(member.guild.id)]
        channel = self.bot.get_channel(channel)
        return await channel.send(embed=embed)

    # @bot.event
    # async def on_member_join(member):
    #     channel = bot.get_channel(751137949420224645)
    #     await channel.send(member.mention + " has entered!")


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(title=str(member.display_name)+' has left ' +
                            str(member.guild.name), color=random.randint(0, 0xffffff))
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()

        with open("guild.json", "r") as f:
            guildInfo = json.load(f)
            f.close()
        channel = guildInfo[str(member.guild.id)]
        channel = self.bot.get_channel(channel)
        return await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.id) == '764120247875272734' or str(message.channel.id) == '751140561255268423':
            return
        if str(message.guild.id) == '765941083254947911':
            return
        now = datetime.datetime.utcnow()
        current_time = now.strftime("%H:%M|%m/%d/%Y")
        if message.author.id != self.bot.user.id:
            print(
                f"{message.guild}/{message.channel}/  {current_time}  /{message.author.name}>{message.content}  ")
            if message.embeds:
                for embed in message.embeds:
                    print(embed.to_dict())

    @commands.command(aliases=['m'], brief='Mutes someone, need manage roles')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, user: Optional[discord.Member], everyone=None):
        if everyone == 'everyone':
            async with ctx.typing():
                try:
                    r = get(ctx.message.guild.roles, name='Muted')
                    for person in ctx.message.guild.members:
                        u = ctx.guild.get_member(person.id)
                        await u.add_roles(r)
                    return await ctx.send(f'Muted everyone')
                except AttributeError:
                    Muted = await ctx.guild.create_role(name="Muted", hoist = True)
                    for channel in ctx.guild.channels:  # removes permission to view and send in the channels
                        await channel.set_permissions(Muted, send_messages=False,
                                                      read_message_history=False,
                                                      read_messages=False)
                    role = get(user.guild.roles, name='Muted')
                    for person in ctx.message.guild.members:
                        u = ctx.guild.get_member(person.id)
                        await u.add_roles(role)
                    return await ctx.send(f'Created Muted role and muted Everyone')

                except discord.Forbidden:
                    return await ctx.send('I\'m not allowed to do that')
        else:
            try:
                role = get(user.guild.roles, name='Muted')
                await user.add_roles(role)
                await ctx.send(f'`{user.display_name}` has been muted from chat')
            except BadArgument:
                return await ctx.send(f'`{user.display_name}` user not found')
            except discord.Forbidden:
                return await ctx.send('I\'m not allowed to do that')
            except AttributeError:
                Muted = await ctx.guild.create_role(name="Muted", hoist = True)
                for channel in ctx.guild.channels:  # removes permission to view and send in the channels
                    await channel.set_permissions(Muted, send_messages=False,
                                                read_message_history=False,
                                                read_messages=False)
                role = get(user.guild.roles, name='Muted')
                await user.add_roles(role)
                return await ctx.send(f'Created Muted role and muted `{user.display_name}`')

    @commands.command(aliases=['um'], brief='Unmutes someone, need manage roles')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, user: Optional[discord.Member], everyone=None):
        if everyone == 'everyone':
            async with ctx.typing():
                try:
                    r = get(ctx.message.guild.roles, name='Muted')
                    for person in ctx.message.guild.members:
                        u = ctx.guild.get_member(person.id)
                        await u.remove_roles(r)
                    return await ctx.send(f'Unmuted everyone')

                except discord.Forbidden:
                    return await ctx.send('I\'m not allowed to do that')
        try:
            role = get(user.guild.roles, name='Muted')
            await user.remove_roles(role)
            await ctx.send(f'{user.display_name} has been unmuted')
        except BadArgument:
            return await ctx.send(f'`{user.display_name}` user not found')
        except discord.Forbidden:
            return await ctx.send('I\'m not allowed to do that')
        except AttributeError:
            return await ctx.send('`Muted` is not a role, use ;mute member to create the muted role')

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
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def blacklistadd(self, ctx, user: discord.Member=None):
        if user==None:
            return await ctx.send('Input a user to add to blacklist')
        else:
            with open('blacklist.json', 'r') as blacklist:
                people = json.load(blacklist)
                if str(user.id) in people['list']:
                    return await ctx.send('User already in blacklist')
                else:
                    people['list'].append(str(user.id))
                blacklist.close()
            with open('blacklist.json', 'w') as blacklist:
                json.dump(people, blacklist)
                blacklist.close()
        return await ctx.send(f'{user.display_name} has been added to the blacklist')

    @commands.command(aliases=['br'], brief='Removes someone to a blacklist so they can use commands again')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def blacklistremove(self, ctx, user: discord.Member = None):
        if user == None:
            return await ctx.send('Input a user to remove from blacklist')
        else:
            with open('blacklist.json', 'r') as blacklist:
                people = json.load(blacklist)
                if str(user.id) not in people['list']:
                    return await ctx.send('User not in blacklist')
                else:
                    people['list'].remove(str(user.id))
                blacklist.close()
            with open('blacklist.json', 'w') as blacklist:
                json.dump(people, blacklist)
                blacklist.close()
        return await ctx.send(f'{user.display_name} has been removed from the blacklist')

    @commands.command(aliases=['bls'], brief='Shows the people in the blacklist')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def blacklistshow(self, ctx, user: discord.Member = None):
        with open('blacklist.json', 'r') as blacklist:
            people = json.load(blacklist)
            blacklist.close()
        embed = discord.Embed(title='Blacklisted People', color = random.randint(0, 0xffffff))
        embed.set_author(name=ctx.author.display_name,
                        icon_url=ctx.author.avatar_url)

        embed.timestamp = datetime.datetime.utcnow()
        
        if len(people['list']) == 0:
            return await ctx.send('No blacklisted people!')
        n=1
        for userid in people['list']:
            user = self.bot.get_user(int(userid))
            embed.add_field(name=f'{n})', value = f'{user.name}')
        return await ctx.send(embed=embed)
                
    @commands.command(aliases=["slowm"], brief="Custom Slow Mode")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, slowmode: int):
        if slowmode > 21600:
            await ctx.send("Slow Mode too long")
        else:
            await ctx.channel.edit(slowmode_delay=slowmode)
            return await ctx.send(
                f"Slow Mode set to {slowmode} seconds for {ctx.channel.mention}")

    @commands.command(brief="See your or other peoples permissions", aliases=["permissions"])
    @commands.cooldown(1, 5, commands.BucketType.user)
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

    @commands.command(description="Blocks a user from chatting in current channel")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def block(self, ctx, *, user: discord.Member):
        try:
            await ctx.channel.set_permissions(
                user, send_messages=False
            )
            return await ctx.send(f"Blocked {user.mention} from sending messages in **{ctx.channel.name}**")
        except discord.Forbidden:
            return await ctx.send("I don\'t have permissions to do that")

    @commands.command(description="Unblocks a user from current channel")
    @commands.cooldown(1, 5, commands.BucketType.user)
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
        aliases=["delete", "erase"],
        brief="Clears a certain amount of messages"
    )
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def purge(self, ctx, amount: int, *, member: discord.Member = None):
        def check(message):
            return message.author.id == member.id

        if not member:
            deleted = await ctx.channel.purge(limit=(amount+1))
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
            deleted = await ctx.channel.purge(
                limit=amount,
                check=check,

            )
            await ctx.message.delete()
            return await ctx.send(
                f"Deleted **{len(deleted)}** messages by **{member}**", delete_after=10
            )


    @commands.command(brief='Deletes Kookies\' messages after a certain amount of seconds')
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def prune(self, ctx, time = 60):
        with open('config.json', 'r') as config:
            info = json.load(config)
            info['prune'] = not info['prune']
            info['time'] = str(time)
            config.close()
        with open ('config.json', 'w') as config:
            json.dump(info, config)
            config.close()
        time = info['time']
        if info['prune']:
            message = 'Kookies\' responses will now be deleted after '+ str(time) + ' seconds'
        else:
            message = 'Pruning is now off'
        return await ctx.send(message)


    @commands.command(brief="Bans a user")
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ban(self, ctx, *, member: discord.Member):
        await member.ban()
        return await ctx.send(f"Banned {member.mention}")

    @commands.command(
        brief="Unbans a previously banned user with their name and discriminator"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
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
            await ctx.send("User not found")

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
