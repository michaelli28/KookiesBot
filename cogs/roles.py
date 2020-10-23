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
from pytz import timezone
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
        if r == 'Admin' or r == 'Admin but Lower':
            if str(ctx.author.id) != '587068610237693963':
                return await ctx.send('Only owner can give admin permissions')
        if everyone == 'everyone':
            async with ctx.typing():
                try:
                    r = get(ctx.guild.roles, name=r)
                    
                    for person in ctx.guild.members:
                        u = ctx.guild.get_member(person.id)
                        await u.add_roles(r)
                    return await ctx.send(f'Gave everyone the {r} role')
                except AttributeError:
                    return await ctx.send('That is not a valid role')
                except discord.Forbidden:
                    return await ctx.send('I\'m not allowed to do that')
        else:
            try:
                r = get(ctx.guild.roles, name=r)
                if r in user.roles:
                    return await ctx.send(f'{user.display_name} already has role {role}')
                else:
                    await user.add_roles(r)
                    return await ctx.send(f'`{r}` role was given to `{user.display_name}`')
            except AttributeError:
                return await ctx.send('That is not a valid role')
            except BadArgument:
                return await ctx.send(f'`{user.display_name}` user not found')
            except discord.Forbidden:
                return await ctx.send('I\'m not allowed to do that')

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
        if r == 'Admin' or r == 'Admin but Lower':
            if str(ctx.author.id) != '587068610237693963':
                return await ctx.send('Only owner can remove admin permissions')
        if everyone == 'everyone':
            async with ctx.typing():
                try:
                    r = get(ctx.guild.roles, name=r)
                    if r not in user.roles:
                        return await ctx.send(f'{user.display_name} doesn\'t have role {role}')
                    for person in ctx.guild.members:
                        u = ctx.guild.get_member(person.id)
                        await u.remove_roles(r)
                    return await ctx.send(f'Everyone\'s {r} role has been removed')
                except AttributeError:
                    return await ctx.send('That is not a valid role')
                except discord.Forbidden:
                    return await ctx.send('I\'m not allowed to do that')
        try:
            r = get(ctx.guild.roles, name=r)
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


    @commands.command(aliases=['er'], brief='Edits a role')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def editrole(self, ctx, name, *, newname: Optional[str] = None, position: Optional[int] = None, mentionable: Optional[bool] = None):
        
        # if mentionable != None:
        #         await r.edit(mentionable=mentionable)
        #         await ctx.send(f'Changed the mentionability to `{mentionable}`')

        # if position != None:
        #     await r.edit(position=position)
        #     await ctx.send(f'Changed the position of the role to `{position}`')
        if newname == None:
            return await ctx.send('You need to specify the new name to change to')
        rindex = 0
        for char in name:
            try:
                name.find('_')
                rindex += 1
            except:
                pass
        
        r = name.replace('_', " ", rindex)
        r = get(ctx.message.guild.roles, name=r)
        if r == None:
            return await ctx.send(f'Role {r} doesn\'t exist')
        try:
            await r.edit(name = newname, position = position, mentionable = None)
            if newname != None:
                await ctx.send(f'Changed the name of role {r} to `{newname}`') 
            if position != None:
                await ctx.send(f'Changed the position of role {r} to `{position}`')
            if mentionable != None:
                await ctx.send(f'Changed the mentionability of role {r} to `{mentionable}`')
            return
        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')


    @commands.command(aliases=['rh'], brief='Sets the role hoist (shown separately on member list or not)')
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    async def rolehoist(self, ctx, name, hoist: Optional[bool] = None):
        if hoist == None:
            return await ctx.send('You need to specify if the role is shown separately in the memberlist')
        if hoist.lower() == 'true':
            hoist = True
        if hoist.lower() == 'false':
            hoist = False
        rindex = 0
        for char in name:
            try:
                name.find('_')
                rindex += 1
            except:
                pass

        r = name.replace('_', " ", rindex)
        r = get(ctx.message.guild.roles, name=r)
        if r == None:
            return await ctx.send(f'Role {r} doesn\'t exist')
        try:
            await r.edit(hoist=hoist)
            if hoist != None:
                await ctx.send(f'Changed the hoist of role {r} to {hoist}')
            return

        except discord.Forbidden:
            return await ctx.send('I don\'t have the permissions to do that')
            
    @commands.command(aliases=['rc'], brief='Adds a role claim message, use like this: ;rc toxic pro_player noob with spaces as underscores')
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roleclaim(self, ctx, *roles, note=None):
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
                return await ctx.send(f'`{r}` is not a valid role')

            message += f'React with {reactions[index]} to receive the `{role}` role!\n'
            index += 1
        if note == None:
            embed = Embed(
                title=f"Role Reactions", color=random.randint(0, 0xffffff), description = message)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            timestamp = datetime.datetime.utcnow()
            embed.timestamp = timestamp
            messagesent = await ctx.send(embed=embed)

        else:
            embed = Embed(
                title=f"Role Reactions", color=random.randint(0, 0xffffff), description = f'{note}\n{message}')
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            timestamp = datetime.datetime.utcnow()
            embed.timestamp = timestamp
            messagesent = await ctx.send(embed=embed)

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


    @commands.command(aliases=['rl'], brief='Show a list of roles from highest to lowest level')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rolelist(self, ctx):
        async with ctx.typing():
            roles = ctx.guild.roles
            roles.reverse()
            menu = MenuPages(source=HelpMenu(ctx, roles), delete_message_after=True)
            return await menu.start(ctx)




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
                fields.append((f'{entry.name}', 'No one has this role right now...'))
            else:
                fields.append((f'{entry.name}', memberslist[0:-2]))

        self.place+=1

        return await self.write_page(menu, fields)


def setup(bot):
	bot.add_cog(roles(bot))



