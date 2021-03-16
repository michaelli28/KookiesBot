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
from pytz import timezone
import asyncio
from discord.ext import tasks

from discord.ext.commands.errors import BadArgument
cluster = MongoClient(
                    'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/Other?retryWrites=true&w=majority')
db = cluster.Other
global collection
collection = db['Roles']


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


class roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['ar'], brief='Gives someone a role, need manage roles permission, if the user has a space in the name, mention them or')
    # This must be exactly the name of the appropriate role
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def addrole(self, ctx, user: Union[discord.Member, str], role: discord.Role):
        # rindex = 0
        # for char in role:
        #     try:
        #         role.find('_')
        #         rindex += 1
        #     except:
        #         pass

        # r = role.replace('_', " ", rindex)
        r = role
        if ctx.author.top_role.position <= r.position:
            if str(ctx.author.id) != '587068610237693963':
                return await ctx.send(f'Your role position isn\'t high enough to add role **{r.name}** to members')

        if user == 'everyone':
            async with ctx.typing():
                try:
                    #r = get(ctx.guild.roles, name=r)
                    
                    for person in ctx.guild.members:
                        if r in person.roles:
                            await ctx.send(f'{person.display_name} already has role {r.name}')
                            continue
                        await person.add_roles(r)

                    return await ctx.send(f'Gave everyone the {r} role')
                except AttributeError:
                    return await ctx.send('That is not a valid role')
                except discord.Forbidden:
                    return await ctx.send('I\'m not allowed to do that')
        else:
            try:
                #r = get(ctx.guild.roles, name=r)
                if r in user.roles:
                    return await ctx.send(f'{user.display_name} already has role {r.name}')
                else:
                    await user.add_roles(r)
                    return await ctx.send(f'`{r}` role was given to `{user.display_name}`')
            except AttributeError:
                return await ctx.send('That is not a valid role')
            except BadArgument:
                return await ctx.send(f'`{user.display_name}` user not found')
            except discord.Forbidden:
                return await ctx.send('I\'m not allowed to do that')

    @commands.command(aliases=['rr'], brief='Removes a role, need manage roles')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, user: Union[discord.Member, str], role: discord.Role):
        # rindex = 0
        # for char in role:
        #     try:
        #         role.find('_')
        #         rindex += 1
        #     except:
        #         pass

        # r = role.replace('_', " ", rindex)
        r = role

        if ctx.author.top_role.position <= r.position:
            if str(ctx.author.id) != '587068610237693963':
                return await ctx.send(f'Your role position isn\'t high enough to remove role **{r.name}** from members')
        if user == 'everyone':
            async with ctx.typing():
                try:
                    #r = get(ctx.guild.roles, name=r)                    
                    for person in ctx.guild.members:
                        if r not in person.roles:
                            await ctx.send(f'{person.display_name} doesn\'t have role {r.name}')
                            continue

                        await person.remove_roles(r)
                    return await ctx.send(f'Everyone\'s {r} role has been removed')
                except AttributeError:
                    return await ctx.send('That is not a valid role')
                except discord.Forbidden:
                    return await ctx.send('I\'m not allowed to do that')
        try:
            #r = get(ctx.guild.roles, name=r)
            await user.remove_roles(r)
            await ctx.send(f'`{r}` role was removed from `{user.display_name}`')
        except AttributeError:
            return await ctx.send('That is not a valid role')
        except BadArgument:
            return await ctx.send(f'`{user}` user not found')
        except discord.Forbidden:
            return await ctx.send('I\'m not allowed to do that')


    @commands.command(aliases=['cr'], brief='Creates a role; Using `random` for color sets a random color')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx, name, color=None, permission=None):
        rindex = 0
        for _ in name:
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
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def deleterole(self, ctx, role: discord.Role):
        if ctx.author.top_role.position <= role.position:
            if str(ctx.author.id) != '587068610237693963':
                return await ctx.send(f'Your role position isn\'t high enough to delete role **{role.name}**')
        try:
            await role.delete()
            return await ctx.send(f'Deleted the role `{role.name}`')
        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')


    @commands.command(aliases=['rn'], brief='Edits a role\'s name')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def rolename(self, ctx, role: discord.Role, newname: str = None):
        
        # if mentionable != None:
        #         await r.edit(mentionable=mentionable)
        #         await ctx.send(f'Changed the mentionability to `{mentionable}`')

        # if position != None:
        #     await r.edit(position=position)
        #     await ctx.send(f'Changed the position of the role to `{position}`')
        
        if newname == None:
            return await ctx.send('You need to specify the new name to change to')
        # rindex = 0
        # for _ in name:
        #     try:
        #         name.find('_')
        #         rindex += 1
        #     except:
        #         pass
        
        # r = name.replace('_', " ", rindex)
        # r = get(ctx.message.guild.roles, name=r)
        # if r == None:
        #     return await ctx.send(f'{name} is not a role')
        
        r = role
        pname = r.name
        if ctx.author.top_role.position <= r.position:
            if str(ctx.author.id) != '587068610237693963':
                return await ctx.send(f'Your role position isn\'t high enough to rename role **{r.name}**')
        try:
            await r.edit(name = newname)
            if newname != None:
                await ctx.send(f'Changed the name of role {pname} to `{newname}`') 
            return
        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')

    @commands.command(aliases=['rp'], brief='Edits a role\'s position')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def roleposition(self, ctx, role: discord.Role, position: int = None):
        if position == None:
            return await ctx.send('You need to specify the new position to change to')
        # rindex = 0
        
        # for _ in name:
        #     try:
        #         name.find('_')
        #         rindex += 1
        #     except:
        #         pass
        
        # r = name.replace('_', " ", rindex)
        # r = get(ctx.message.guild.roles, name=r)
        r=role
        ppos = r.position
        if ctx.author.top_role.position <= r.position or ctx.author.top_role.position <= position:
            return await ctx.send(f'You do not have permissions to change this role. Your top role position **{ctx.author.top_role.position}** is less than or equal to {r.name}\'s (**{r.position}**) or the position you are trying to change {r.name} to is more than or equal to your role position ')
        # if r == None:
        #     return await ctx.send(f'{name} is not a role')
        try:
            await r.edit(position = position)

            if position != None:
                await ctx.send(f'Changed the position of role {r} from {ppos} to `{position}`')
            return
        except discord.errors.HTTPException:
            return await ctx.send('Missing permissions')
    @commands.command(aliases=['rm'], brief='Edits a role\'s mentionability')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def rolemention(self, ctx, role: discord.Role, mentionable: bool = None):

        if mentionable == None:
            return await ctx.send('You need to specify the new mentionability to change to')
        # rindex = 0
        # for _ in name:
        #     try:
        #         name.find('_')
        #         rindex += 1
        #     except:
        #         pass
        
        # r = name.replace('_', " ", rindex)
        # r = get(ctx.message.guild.roles, name=r)
        # if r == None:
        #     return await ctx.send(f'{name} is not a role')
        r = role
        if ctx.author.top_role.position <= r.position:
            if str(ctx.author.id) != '587068610237693963':
                return await ctx.send(f'Your role position isn\'t high enough to change role mentionability of role **{r.name}**')
        try:
            await r.edit(mentionable = mentionable)
            if mentionable != None:
                await ctx.send(f'Changed the mentionability of role {r} to `{mentionable}`')
            return
        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')

    @commands.command(aliases=['rh'], brief='Sets the role hoist (shown separately on member list or not)')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def rolehoist(self, ctx, role: discord.Role, hoist: bool = None):
        if hoist == None:
            return await ctx.send('You need to specify if the role is shown separately in the memberlist')

        # rindex = 0
        # for _ in name:
        #     try:
        #         name.find('_')
        #         rindex += 1
        #     except:
        #         pass

        # r = name.replace('_', " ", rindex)
        # r = get(ctx.message.guild.roles, name=r)
        # if r == None:
        #     return await ctx.send(f'{name} is not a role')
        r=role
        if ctx.author.top_role.position <= r.position:
            if str(ctx.author.id) != '587068610237693963':
                return await ctx.send(f'Your role position isn\'t high enough to change role hoist of role **{r.name}**')
        try:
            await r.edit(hoist=hoist)
            if hoist != None:
                await ctx.send(f'Changed the hoist of role {r} to {hoist}')
            return

        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')

    @commands.command(aliases=['rc'], brief='Adds a role claim message, put 2 quotation marks around roles with spaces like this: ;rc toxic "person 1" "discord user" person2')
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def roleclaim(self, ctx, *roles: discord.Role):
        await ctx.message.delete()
        if 1 > len(roles) > 10:
            return await ctx.send('List of roles must be between 1 and 10')

        global rolesR
        rolesR = list(roles)

        # with open("roles.json", "r") as f:
        #     rolesjson = json.load(f)
        #     f.close()


        index = 0
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣',
                    '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        message = ''
        # rindex = 0

        # for r in rolesR:
        #     for char in r:
        #         try:
        #             r.find('_')
        #             rindex += 1
        #         except:
        #             pass

        #     r = r.replace('_', " ", rindex)
        #     #rolesR[index] = r

        #     role = get(ctx.guild.roles, name=r)
            
        #     if role == None:
        #         return await ctx.send(f'`{r}` is not a valid role')
        for role in rolesR:
            if ctx.author.top_role.position <= role.position:
                return await ctx.send(f'Your role position isn\'t high enough to make a role claim for role **{role.name}**')
                    
            rolesR[index] = role.id
            message += f'React with {reactions[index]} to receive the `{role.name}` role!\n'
            index += 1

        # if note == None:
        embed = Embed(
            title=f"Role Reactions", color=random.randint(0, 0xffffff), description = message)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        timestamp = datetime.datetime.utcnow()
        embed.timestamp = timestamp
        messagesent = await ctx.send(embed=embed)

        # else:
        #     embed = Embed(
        #         title=f"Role Reactions", color=random.randint(0, 0xffffff), description = f'{note}\n{message}')
        #     embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        #     timestamp = datetime.datetime.utcnow()
        #     embed.timestamp = timestamp
        #     messagesent = await ctx.send(embed=embed)

        collection.insert_one({'_id':str(messagesent.id),'roles':rolesR})

        # with open("roles.json", "w") as f:
        #     json.dump(rolesjson, f)
        #     f.close()
        for i in range(len(roles)):
            await messagesent.add_reaction(reactions[i])
        return



    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = discord.utils.get(self.bot.get_all_channels(), id=payload.channel_id)
        user = payload.member
        guild = self.bot.get_guild(payload.guild_id)
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
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            if (not payload.member.bot):
                user = payload.member
                #role = get(user.guild.roles, name=rolesR[0])
                role = guild.get_role(rolesR[0])
                if role in user.roles:
                    return await user.send(f'You already have role **{role.name}** in **{user.guild.name}**')
                await user.add_roles(role)
                return await user.send(f'You have received the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '2️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            if (not payload.member.bot):
                user = payload.member
                role = guild.get_role(rolesR[1])
                if role in user.roles:
                    return await user.send(f'You already have role **{role.name}** in **{user.guild.name}**')
                await user.add_roles(role)
                return await user.send(f'You have received the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '3️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            if (not payload.member.bot):
                user = payload.member
                role = guild.get_role(rolesR[2])
                if role in user.roles:
                    return await user.send(f'You already have role **{role.name}** in **{user.guild.name}**')
                await user.add_roles(role)
                return await user.send(f'You have received the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '4️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            if (not payload.member.bot):
                user = payload.member
                role = guild.get_role(rolesR[3])
                if role in user.roles:
                    return await user.send(f'You already have role **{role.name}** in **{user.guild.name}**')
                await user.add_roles(role)
                return await user.send(f'You have received the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '5️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            if (not payload.member.bot):
                user = payload.member
                role = guild.get_role(rolesR[4])
                if role in user.roles:
                    return await user.send(f'You already have role **{role.name}** in **{user.guild.name}**')
                await user.add_roles(role)
                return await user.send(f'You have received the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '6️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            if (not payload.member.bot):
                user = payload.member
                role = guild.get_role(rolesR[5])
                if role in user.roles:
                    return await user.send(f'You already have role **{role.name}** in **{user.guild.name}**')
                await user.add_roles(role)
                return await user.send(f'You have received the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '7️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            if (not payload.member.bot):
                user = payload.member
                role = guild.get_role(rolesR[6])
                if role in user.roles:
                    return await user.send(f'You already have role **{role.name}** in **{user.guild.name}**')
                await user.add_roles(role)
                return await user.send(f'You have received the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '8️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            if (not payload.member.bot):
                user = payload.member
                role = guild.get_role(rolesR[7])
                if role in user.roles:
                    return await user.send(f'You already have role **{role.name}** in **{user.guild.name}**')
                await user.add_roles(role)
                return await user.send(f'You have received the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '9️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            if (not payload.member.bot):
                user = payload.member
                role = guild.get_role(rolesR[8])
                if role in user.roles:
                    return await user.send(f'You already have role **{role.name}** in **{user.guild.name}**')
                await user.add_roles(role)
                return await user.send(f'You have received the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '🔟':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            if (not payload.member.bot):
                user = payload.member
                role = guild.get_role(rolesR[9])
                if role in user.roles:
                    return await user.send(f'You already have role **{role.name}** in **{user.guild.name}**')
                await user.add_roles(role)
                return await user.send(f'You have received the role **{role.name}** in **{user.guild.name}**')


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        if payload.emoji.name == '1️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            # role = get(guild.roles, name=rolesR[0])
            role = guild.get_role(rolesR[0])
            if role not in user.roles:
                return await user.send(f'You don\'t have role **{role.name}** in **{user.guild.name}**')
            await user.remove_roles(role)
            return await user.send(f'You have successfully removed the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '2️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = guild.get_role(rolesR[1])
            if role not in user.roles:
                return await user.send(f'You don\'t have role **{role.name}** in **{user.guild.name}**')
            await user.remove_roles(role)
            return await user.send(f'You have successfully removed the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '3️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = guild.get_role(rolesR[2])
            if role not in user.roles:
                return await user.send(f'You don\'t have role **{role.name}** in **{user.guild.name}**')
            await user.remove_roles(role)
            return await user.send(f'You have successfully removed the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '4️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = guild.get_role(rolesR[3])
            if role not in user.roles:
                return await user.send(f'You don\'t have role **{role.name}** in **{user.guild.name}**')
            await user.remove_roles(role)
            return await user.send(f'You have successfully removed the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '5️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = guild.get_role(rolesR[4])
            if role not in user.roles:
                return await user.send(f'You don\'t have role **{role.name}** in **{user.guild.name}**')
            await user.remove_roles(role)
            return await user.send(f'You have successfully removed the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '6️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = guild.get_role(rolesR[5])
            if role not in user.roles:
                return await user.send(f'You don\'t have role **{role.name}** in **{user.guild.name}**')
            await user.remove_roles(role)
            return await user.send(f'You have successfully removed the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '7️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = guild.get_role(rolesR[6])
            if role not in user.roles:
                return await user.send(f'You don\'t have role **{role.name}** in **{user.guild.name}**')
            await user.remove_roles(role)
            return await user.send(f'You have successfully removed the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '8️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = guild.get_role(rolesR[7])
            if role not in user.roles:
                return await user.send(f'You don\'t have role **{role.name}** in **{user.guild.name}**')
            await user.remove_roles(role)
            return await user.send(f'You have successfully removed the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '9️⃣':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = guild.get_role(rolesR[8])
            if role not in user.roles:
                return await user.send(f'You don\'t have role **{role.name}** in **{user.guild.name}**')
            await user.remove_roles(role)
            return await user.send(f'You have successfully removed the role **{role.name}** in **{user.guild.name}**')
        elif payload.emoji.name == '🔟':
            # with open("roles.json", "r") as f:
            #     rolesjson = json.load(f)
            #     f.close()
            # rolesR = rolesjson[str(payload.message_id)]
            result = collection.find_one({'_id':str(payload.message_id)})
            rolesR = result['roles']
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            role = guild.get_role(rolesR[9])
            if role not in user.roles:
                return await user.send(f'You don\'t have role **{role.name}** in **{user.guild.name}**')
            await user.remove_roles(role)
            return await user.send(f'You have successfully removed the role **{role.name}** in **{user.guild.name}**')


    @commands.command(aliases=['rl'], brief='Show a list of roles from highest to lowest level')
    @commands.cooldown(times, cooldown, commands.BucketType.user)
    async def rolelist(self, ctx):
        async with ctx.typing():
            roles = ctx.guild.roles
            roles.reverse()
            menu1 = menu(source=HelpMenu(ctx, roles))
            return await menu1.start(ctx)



class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        self.place = 1
        super().__init__(data, per_page=5)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(
                title=f"List of roles for {self.ctx.guild.name}", color=random.randint(0, 0xffffff))
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(
                text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} roles")
        timestamp = datetime.datetime.utcnow()
        embed.timestamp = timestamp
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        for entry in entries:
            memberslist = ''
            for member in entry.members:
                memberslist += member.display_name + ', '
            if memberslist == '':
                fields.append((f'{entry.name} - {entry.position}', 'No one has this role right now...'))
            else:
                fields.append((f'{entry.name} - {entry.position}', memberslist[0:-2]))

        self.place+=1

        return await self.write_page(menu, fields)


def setup(bot):
	bot.add_cog(roles(bot))



