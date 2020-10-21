
import discord
from discord.ext import commands
from time import sleep
import pyprog
from discord.ext import tasks, commands
import datetime
import pytz


'''
class MyCog(commands.Cog):
    def __init__(self):
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5.0)
    async def printer(self):
        print(self.index)
        self.index += 1
def setup(bot):
    bot.add_cog(MyCog(bot))

bot = commands.Bot(command_prefix=';', caseInsensitive=True,
                   description='Kookies FOR THE WIN')


@bot.event
async def on_ready():      
    print('Logged in as:\n{0.user.name}'.format(bot))
@bot.command()
async def spam(ctx):
  for i in range(100):
      await ctx.send('SPAMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM')
bot.run('NzQzODU5NDIwNzk4MTI0MDQz.XzazEg.H8jmotH113mVSyRdNnU76aZ1P74')


# Create Object
prog = pyprog.ProgressBar(" ", " ", total=5, bar_length=26, complete_symbol="=", not_complete_symbol=" ",
            wrap_bar_prefix=" [", wrap_bar_suffix="] ", progress_explain="", progress_loc=pyprog.ProgressBar.PROGRESS_LOC_END)
# Update Progress Bar
prog.update()

for i in range(5):
# Do something
    sleep(1)
# Set current status
    prog.set_stat(i + 1)
# Update Progress Bar again
prog.update()

# Make the Progress Bar final
prog.end()

import pymongo
from pymongo import MongoClient
import random
cluster = MongoClient(
    'mongodb+srv://Kookies:Kookies@kookiesxp.b3brr.mongodb.net/KookiesBot?retryWrites=true&w=majority')
db = cluster['KookiesBot']
global collection
collection = db['Xp']
#try:
#    collection.update_one({'_id': 'id1'}, {"$inc": {"Xp": random.randint(15, 25)}})
#except:
collection.insert_one({'_id': 'id4', 'name': 'cool', "Xp": random.randint(15, 25)})
'''


def day(y, m, d):
    t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
    y -= m < 3
    print(y)
    v = (y + y/4 - y/100 + y/400 + t[m-1] + d) % 7
    days = ['Sunday', 'Monday', 'Tuesday',
            'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return days[int(v)]

#print(day(2006, 2, 3))


timestamp = datetime.datetime.now()
print(timestamp)
timeEastern = pytz.timezone('US/Eastern').localize(timestamp)
print(timeEastern)
