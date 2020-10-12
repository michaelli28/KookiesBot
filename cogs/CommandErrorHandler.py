import discord
import traceback
import sys
from discord.ext import commands
import random

class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        # get the original exception
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            if ctx.message.content.startswith(';)'):
                return
            await ctx.send(f'`{ctx.message.content}` is not a valid command')

        elif isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace(
                'guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format(
                    "**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'I need the **{}** permission(s) to run this command.'.format(
                fmt)
            await ctx.send(_message)
            return

        # elif isinstance(error, commands.DisabledCommand):
        #     await ctx.send('This command has been disabled.')
        #     return
        elif isinstance(error, discord.errors.Forbidden):
            return await ctx.send('I don\'t have permissions to do that')
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.delete()
            await ctx.send('{}, That command is on cooldown! Try again in {:.2f}s!'.format(ctx.author.mention, error.retry_after))

        elif isinstance(error, commands.NotOwner):
            await ctx.message.delete()
            return await ctx.send('{}, That command is for the owner of the bot only (NotThatBot#3360)'.format(ctx.author.mention))
            
        elif isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').replace(
                'guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format(
                    "**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'You need the **{}** permission(s) to use this command.'.format(
                fmt)
            return await ctx.send(_message)


        elif isinstance(error, commands.UserInputError):
            await ctx.send("Invalid input")

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except discord.Forbidden:
                pass
            return

        # elif isinstance(error, commands.CheckFailure):
        #     await ctx.send("You do not have permission to use this command")


        # ignore all other exception types, but print them to stderr
        print('Ignoring exception in command {}:'.format(
            ctx.command), file=sys.stderr)

        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)




        # ignored = (commands.CommandNotFound, )

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        # error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        # if isinstance(error, ignored):
        #     return



        # For this error example we check to see where it came from...
        # if isinstance(error, commands.BadArgument):
        #     if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
        #         await ctx.send('I could not find that member. Please try again.')

        # if isinstance(error, commands.MissingPermissions):
        #     missing = [perm.replace('_', ' ').replace(
        #         'guild', 'server').title() for perm in error.missing_perms]
        #     if len(missing) > 2:
        #         fmt = '{}, and {}'.format(
        #             "**, **".join(missing[:-1]), missing[-1])
        #     else:
        #         fmt = ' and '.join(missing)
        #     _message = 'You need the **{}** permission(s) to use this command.'.format(
        #         fmt)
        #     await ctx.send(_message)
        #     return
            
        #else:
            #All other Errors not returned come here. And we can just print the default TraceBack.
            # print('Ignoring exception in command {}:'.format(
            #     ctx.command), file=sys.stderr)
            # traceback.print_exception(
            #     type(error), error, error.__traceback__, file=sys.stderr)


    """Below is an example of a Local Error Handler for our command do_repeat"""
    
    @commands.command(name='repeat', brief='Repeats your input')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def do_repeat(self, ctx, *, inp: str):
        """A simple command which repeats your input!
        Parameters
        ------------
        inp: str
            The input you wish to repeat.
        """
        message = ctx.message
        await message.delete()
        return await ctx.send(inp)

    @do_repeat.error
    async def do_repeat_handler(self, ctx, error):
        """A local Error Handler for our command do_repeat.
        This will only listen for errors in do_repeat.
        The global on_command_error will still be invoked after.
        """

        # Check if our required argument inp is missing.
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'inp':
                return await ctx.send("You forgot to give me input to repeat!")


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
