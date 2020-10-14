from typing import Optional

from discord import Embed
from discord.utils import get
from discord.ext.menus import MenuPages, ListPageSource
from discord.ext.commands import Cog
from discord.ext import commands
import random
import datetime
PREFIX=';'
def syntax(command):
    cmd_and_aliases = "|;".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"[{key}]")

    params = " ".join(params)

    return f"`<;{cmd_and_aliases}> {params}`"


def param(command):
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"[{key}]")

    params = " ".join(params)

    return f"`{params}`"


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=5)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page*self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title="Help", description="<cmd|alias|alias> [arg][arg]",  color=random.randint(0, 0xffffff))
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} commands.")
        embed.timestamp = datetime.datetime.now()
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []

        for entry in entries:
            fields.append((entry.brief or "No description", syntax(entry)))

        return await self.write_page(menu, fields)


class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        embed = Embed(title=f"Help with `{command}`",
                description=syntax(command),
                    color=random.randint(0, 0xffffff))
        embed.add_field(name="Command description:", value=command.brief)
        if param(command)=='``':
            
            for cog in self.bot.cogs:
                cogC = self.bot.get_cog(cog)
                for commandC in cogC.get_commands():
                    if str(commandC.name) == str(command):
                        commandCog = cogC.qualified_name
                        embed.add_field(name='Category:', value=f'**{commandCog}**')

            embed.add_field(name='Usage:', value='**'+PREFIX+str(command)+'**')
        else:
            embed.add_field(name='Usage:', value='**'+PREFIX+str(command)+'** '+ str(param(command)))
            for cog in self.bot.cogs:
                cogC = self.bot.get_cog(cog)
                for commandC in cogC.get_commands():
                    if str(commandC.name) == str(command):
                        commandCog = cogC.qualified_name
                        embed.add_field(name='**Category:**', value=f'**{commandCog}**')
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.timestamp = datetime.datetime.now()
        await ctx.send(embed=embed)

    @commands.command(name="help", brief='Shows help menu')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def show_help(self, ctx, cmd: Optional[str]):
        await ctx.send('Please wait while help arrives from somewhere in the US')
        async with ctx.typing():
            if self.bot.get_cog(cmd)!= None:
                cog = self.bot.get_cog(cmd)
                commands = cog.get_commands()
                menu = MenuPages(source=HelpMenu(ctx, commands),
                                delete_message_after=True)
                await menu.start(ctx)
            


            elif cmd == 'all':
                menu = MenuPages(source=HelpMenu(ctx, list(self.bot.commands)))
                await menu.start(ctx)
            
            elif cmd is None:
                cogs = self.bot.cogs
                full = '**Categories:**\n**all**\n'

                for cog in cogs:
                    cogR = self.bot.get_cog(cog)
                    if len(cogR.get_commands()) != 0:
                        full += f'**{cog}**\n'

                embed = Embed(title="Help! Use ;help <Category> to get help for that category or use ;help all to get a list of all commands", color=random.randint(0, 0xffffff), description = full)

                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                embed.timestamp = datetime.datetime.now()
                return await ctx.send(embed=embed)

            else:
                if command := get(self.bot.commands, name=cmd):
                    await self.cmd_help(ctx, command)

                else:
                    return await ctx.send("That command does not exist")





def setup(bot):
	bot.add_cog(help(bot))
