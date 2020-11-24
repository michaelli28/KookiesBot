
import discord
from discord.ext import commands
from time import sleep
import pyprog
from discord.ext import tasks, commands
import datetime
import pytz


# def day(y, m, d):
#     t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
#     y -= m < 3
#     print(y)
#     v = (y + y/4 - y/100 + y/400 + t[m-1] + d) % 7
#     days = ['Sunday', 'Monday', 'Tuesday',
#             'Wednesday', 'Thursday', 'Friday', 'Saturday']
#     return days[int(v)]

# #print(day(2006, 2, 3))


# timestamp = datetime.datetime.now()
# print(timestamp)
# timeEastern = pytz.timezone('US/Eastern').localize(timestamp)
# print(timeEastern)


list = [1,2,3,4,5]
print(list[2:])