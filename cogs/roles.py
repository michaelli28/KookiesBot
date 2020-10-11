import markovify
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from typing import Optional
import json
import discord
from discord.ext import commands
import datetime
import pymongo
from pymongo import MongoClient
import random
import re
import time

import asyncio
from discord.ext import tasks

from discord.ext.commands.errors import BadArgument

class roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['ar'], brief='Gives someone a role, need manage roles, use _ as spaces')
    # This must be exactly the name of the appropriate role
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def addrole(self, ctx, user: Optional[discord.Member], role, everyone=None):
        rindex = 0
        for char in role:
            try:
                role.find('_')
                rindex += 1
            except:
                pass

        r = role.replace('_', " ", rindex)
        if everyone == 'everyone':
            async with ctx.typing():
                try:
                    r = get(ctx.message.guild.roles, name=r)
                    for person in ctx.message.guild.members:
                        u = ctx.guild.get_member(person.id)
                        await u.add_roles(r)
                    return await ctx.send(f'Gave everyone the {r} role')
                except AttributeError:
                    return await ctx.send('That is not a valid role')
                except discord.Forbidden:
                    return await ctx.send('I\'m not allowed to do that')
        else:
            try:
                r = get(user.guild.roles, name=r)
                await user.add_roles(r)
                await ctx.send(f'`{r}` role was given to `{user.display_name}`')
            except AttributeError:
                return await ctx.send('That is not a valid role')
            except BadArgument:
                return await ctx.send(f'`{user.display_name}` user not found')
            except discord.Forbidden:
                return await ctx.send('I\'m not allowed to do that')


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
                    Muted = await ctx.guild.create_role(name="Muted", reason="To use for muting")
                    for channel in ctx.guild.channels:  # removes permission to view and send in the channels
                        await channel.set_permissions(Muted, send_messages=False,
                                                    read_message_history=False,
                                                    read_messages=False)
                    role = get(user.guild.roles, name='Muted')
                    for person in ctx.message.guild.members:
                        u = ctx.guild.get_member(person.id)
                        await u.add_roles(role)
                    await ctx.send(f'Muted Everyone')

                except discord.Forbidden:
                    return await ctx.send('I\'m not allowed to do that')
        try:
            role = get(user.guild.roles, name='Muted')
            await user.add_roles(role)
            await ctx.send(f'`{user.display_name}` has been muted from chat')
        except BadArgument:
            return await ctx.send(f'`{user.display_name}` user not found')
        except discord.Forbidden:
            return await ctx.send('I\'m not allowed to do that')
        except AttributeError:
            Muted = await ctx.guild.create_role(name="Muted", reason="To use for muting")
            for channel in ctx.guild.channels:  # removes permission to view and send in the channels
                await channel.set_permissions(Muted, send_messages=False,
                                            read_message_history=False,
                                            read_messages=False)
            role = get(user.guild.roles, name='Muted')
            await user.add_roles(role)
            await ctx.send(f'`{user.display_name}` has been muted from chat')


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


    @commands.command(aliases=['rr'], brief='Removes a role, need manage roles, use _ as spaces')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, user: Optional[discord.Member], role, everyone=None):
        rindex = 0
        for char in role:
            try:
                role.find('_')
                rindex += 1
            except:
                pass

        r = role.replace('_', " ", rindex)
        if everyone == 'everyone':
            async with ctx.typing():
                try:
                    r = get(ctx.message.guild.roles, name=r)
                    for person in ctx.message.guild.members:
                        u = ctx.guild.get_member(person.id)
                        await u.remove_roles(r)
                    return await ctx.send(f'Everyone\'s {r} role has been removed')
                except AttributeError:
                    return await ctx.send('That is not a valid role')
                except discord.Forbidden:
                    return await ctx.send('I\'m not allowed to do that')
        try:
            r = get(user.guild.roles, name=r)
            await user.remove_roles(r)
            await ctx.send(f'`{r}` role was removed from `{user.display_name}`')
        except AttributeError:
            return await ctx.send('That is not a valid role')
        except BadArgument:
            return await ctx.send(f'`{user}` user not found')
        except discord.Forbidden:
            return await ctx.send('I\'m not allowed to do that')


    @commands.command(aliases=['cr'], brief='Creates a role; Using `random` for color sets a random color, use _ as spaces')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx, name, color=None, permission=None):
        rindex = 0
        for char in name:
            try:
                name.find('_')
                rindex += 1
            except:
                pass

        r = name.replace('_', " ", rindex)
        # newname = ''
        # for part in name:
        #     newname += part+' '
        # newname = newname[0:-1]

        if str(color) == 'random' or color == None:
            color = random.randint(0, 0xffffff)

        if permission == None:
            try:
                await ctx.guild.create_role(name=r, reason='Why not', color=discord.Color(int(color)))
                return await ctx.send(f'Created the role `{r}`')
            except discord.Forbidden:
                return await ctx.send('I don\'t have the permissions to do that')
        else:
            try:
                await ctx.guild.create_role(name=r, reason='Why not', color=discord.Color(int(color)), permissions=discord.Permissions(permissions=int(permission)))
                return await ctx.send(f'Created the role `{r}`')
            except discord.Forbidden:
                return await ctx.send('I don\'t have the permissions to do that')

    @commands.command(aliases=['dr'], brief='Deletes a role')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def deleterole(self, ctx, *, role: discord.Role):
        try:
            await role.delete()
            return await ctx.send(f'Deleted the role `{role.name}`')
        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')


    @commands.command(aliases=['er'], brief='Edits a role;  permissions is an integer as well')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def editrole(self, ctx, name, newname: Optional[str] = None, mentionable: Optional[bool]=None, position: Optional[int]=None):
        rindex = 0
        for char in name:
            try:
                name.find('_')
                rindex += 1
            except:
                pass
        
        r = name.replace('_', " ", rindex)
        r = get(ctx.message.guild.roles, name=r)
        try:
            if newname != None:
                await r.edit(name = newname)
                await ctx.send(f'Changed the name to `{newname}`')
            if mentionable != None:
                await r.edit(mentionable=mentionable)
                await ctx.send(f'Changed the mentionability to `{mentionable}`')

            if position != None:
                await r.edit(position=position)
                await ctx.send(f'Changed the position of the role to `{position}`')

        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')

    @commands.command(aliases=['rc'], brief='Adds a role claim message, use like this: ;rc toxic pro_player noob with spaces as underscores')
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roleclaim(self, ctx, *roles, messagea=None):
        await ctx.message.delete()
        if 1 > len(roles) > 10:
            return await ctx.send('List of roles must be between 1 and 10')

        global rolesR
        rolesR = list(roles)

        with open("roles.json", "r") as f:
            rolesjson = json.load(f)
            f.close()
        if str(ctx.message.channel.id) in rolesjson:
            del rolesjson[str(ctx.message.id)]

        index = 0
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣',
                    '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        message = ''
        rindex = 0
        for r in rolesR:

            for char in r:
                try:
                    r.find('_')
                    rindex += 1
                except:
                    pass

            r = r.replace('_', " ", rindex)
            rolesR[index] = r

            role = get(ctx.author.guild.roles, name=r)

            if role == None:
                return await ctx.send(await ctx.send(f'`{r}` is not a valid role'))

            message += f'React with {reactions[index]} to receive the `{role}` role!\n'
            index += 1

        if messagea == None:
            messagesent = await ctx.send(message)
        else:
            messagesent = await ctx.send(message+str(messagea))

        rolesjson[messagesent.id] = rolesR

        with open("roles.json", "w") as f:
            json.dump(rolesjson, f)
            f.close()
        for i in range(len(roles)):
            await messagesent.add_reaction(reactions[i])


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = discord.utils.get(self.bot.get_all_channels(), id=payload.channel_id)
        user = payload.member

        if payload.emoji.name == '❌':
            try:
                message = await channel.fetch_message(payload.message_id)
            except:
                pass
            try:
                if message.content.startswith('React with 1️⃣ to receive the '):
                    try:
                        return await user.send('I can\'t delete that message you just reacted to')
                    except:
                        pass
                else:
                    try:
                        if (not payload.member.bot):
                            try:
                                await message.delete()
                            except:
                                pass
                    except:
                        pass
            except:
                pass
        elif payload.emoji.name == '1️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            if (not payload.member.bot):
                user = payload.member
                role = get(user.guild.roles, name=rolesR[0])
                await user.add_roles(role)
                await user.send('You have received the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '2️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            if (not payload.member.bot):
                user = payload.member
                role = get(user.guild.roles, name=rolesR[1])
                await user.add_roles(role)
                await user.send('You have received the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '3️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            if (not payload.member.bot):
                user = payload.member
                role = get(user.guild.roles, name=rolesR[2])
                await user.add_roles(role)
                await user.send('You have received the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '4️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            if (not payload.member.bot):
                user = payload.member
                role = get(user.guild.roles, name=rolesR[3])
                await user.add_roles(role)
                await user.send('You have received the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '5️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            if (not payload.member.bot):
                user = payload.member
                role = get(user.guild.roles, name=rolesR[4])
                await user.add_roles(role)
                await user.send('You have received the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '6️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            if (not payload.member.bot):
                user = payload.member
                role = get(user.guild.roles, name=rolesR[5])
                await user.add_roles(role)
                await user.send('You have received the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '7️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            if (not payload.member.bot):
                user = payload.member
                role = get(user.guild.roles, name=rolesR[6])
                await user.add_roles(role)
                await user.send('You have received the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '8️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            if (not payload.member.bot):
                user = payload.member
                role = get(user.guild.roles, name=rolesR[7])
                await user.add_roles(role)
                await user.send('You have received the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '9️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            if (not payload.member.bot):
                user = payload.member
                role = get(user.guild.roles, name=rolesR[8])
                await user.add_roles(role)
                await user.send('You have received the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '🔟':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            if (not payload.member.bot):
                user = payload.member
                role = get(user.guild.roles, name=rolesR[9])
                await user.add_roles(role)
                await user.send('You have received the `' + str(role) + '` role in `' + str(user.guild.name)+'`')


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        if payload.emoji.name == '1️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = get(guild.roles, name=rolesR[0])
            await user.remove_roles(role)
            await user.send('You have successfully removed the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '2️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = get(guild.roles, name=rolesR[1])
            await user.remove_roles(role)
            await user.send('You have successfully removed the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '3️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = get(guild.roles, name=rolesR[2])
            await user.remove_roles(role)
            await user.send('You have successfully removed the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '4️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = get(guild.roles, name=rolesR[3])
            await user.remove_roles(role)
            await user.send('You have successfully removed the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '5️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = get(guild.roles, name=rolesR[4])
            await user.remove_roles(role)
            await user.send('You have successfully removed the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '6️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = get(guild.roles, name=rolesR[5])
            await user.remove_roles(role)
            await user.send('You have successfully removed the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '7️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = get(guild.roles, name=rolesR[6])
            await user.remove_roles(role)
            await user.send('You have successfully removed the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '8️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = get(guild.roles, name=rolesR[7])
            await user.remove_roles(role)
            await user.send('You have successfully removed the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '9️⃣':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = get(guild.roles, name=rolesR[8])
            await user.remove_roles(role)
            await user.send('You have successfully removed the `' + str(role) + '` role in `' + str(user.guild.name)+'`')
        elif payload.emoji.name == '🔟':
            with open("roles.json", "r") as f:
                rolesjson = json.load(f)
                f.close()
            rolesR = rolesjson[str(payload.message_id)]
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = get(guild.roles, name=rolesR[9])
            await user.remove_roles(role)
            await user.send('You have successfully removed the `' + str(role) + '` role in `' + str(user.guild.name)+'`')


    @commands.command(aliases=['sm'], brief='Server mute everyone in a voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_any_role('Admin', 'Admin but lower')
    async def servermute(self, ctx):
        async with ctx.typing():
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
            for member in channel.members:
                await member.edit(mute=True)
            return await ctx.send('Everyone has been muted')


    @commands.command(aliases=['su'], brief='Unmutes everyone in a voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_any_role('Admin', 'Admin but lower')
    async def serverunmute(self, ctx):
        async with ctx.typing():
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
            for member in channel.members:
                await member.edit(mute=False)
            return await ctx.send('Everyone has been unmuted')


    @commands.command(aliases=['sd'], brief='Server deafen everyone in a voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_any_role('Admin', 'Admin but lower')
    async def serverdeafen(self, ctx):
        async with ctx.typing():
            if ctx.author.voice and ctx.author.voice.channel:
                channel = ctx.author.voice.channel
            for member in channel.members:
                await member.edit(deafen=True)
            return await ctx.send('Everyone has been deafened')


    @commands.command(aliases=['sud'], brief='Undeafens everyone in a voice channel')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_any_role('Admin', 'Admin but lower')
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
        await ctx.send(f'Nickname was changed for {member.mention} from {old} to {nick}')

    
    @commands.command(brief='Locks the server from messages')
    @commands.has_permissions(administrator=True)
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
    @commands.has_permissions(administrator=True)
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
    @commands.has_permissions(administrator=True)
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
    @commands.has_permissions(administrator=True)
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
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def createchannel(self, ctx, name):
        guild = ctx.message.guild
        await guild.create_text_channel(name)

    @commands.command(brief='Creates a voice channel')
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def createvoicechannel(self, ctx, name):
        guild = ctx.message.guild
        await guild.create_voice_channel(name)


    @commands.command(brief='Edits a text channel')
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def editchannel(self, ctx, name: discord.TextChannel, nname: Optional[str] = None, slowmode: Optional[int] = None):
        if nname != None:
            await name.edit(name=nname)
            await ctx.send(f'Changed the name of channel {name.name} to {nname}')
        if slowmode != None:
            await name.edit(slowmode_delay=slowmode)
            await ctx.send(f'Set the slowmode delay for channel {name.name} to {slowmode} seconds')

    @commands.command(brief='Creates a category')
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def createcategory(self, ctx, name):
        guild = ctx.message.guild
        await guild.create_category(name)
        return await ctx.send(f'Created category {name}')

def setup(bot):
	bot.add_cog(roles(bot))



