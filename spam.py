import os

# import discord
# from discord.ext import commands
# from time import sleep
# import pyprog
# from discord.ext import tasks, commands
# import datetime
# import pytz
# import random

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


# list = [1,2,3,4,5]
# print(list[2:])
# import yaml
import asyncio
import random
import re
import requests
import discord
from collections import OrderedDict
import datetime
import youtube_dl
from async_timeout import timeout
from discord.ext import commands
import httpx
from bs4 import BeautifulSoup 
import discord
from discord.ext.menus import MenuPages, ListPageSource
from discord.utils import get
from discord import Embed
from discord.ext import commands
from typing import Optional
#import pyprog
from time import sleep
from pytz import timezone
import aiohttp
from googleapiclient.discovery import build


#coding: utf-8
import json
# Spotify library.
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
# URL conversions.
import urllib.request
import bs4
# Youtube stuff.
import youtube

# Opening our JSON configuration file (which has our tokens).
# with open("config.json", encoding='utf-8-sig') as json_file:
#     APIs = json.load(json_file)

def getTracks(playlistURL):
    # Creating and authenticating our Spotify app.
    # client_credentials_manager = SpotifyClientCredentials(APIs["spotify"]["client_id"], APIs["spotify"]["client_secret"])
    client_credentials_manager = SpotifyClientCredentials(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Getting a playlist.
    results = spotify.user_playlist_tracks(user="",playlist_id=playlistURL)
    # print(results)

    # print (yaml.dump(results['items'], default_flow_style=False))
    print (json.dumps(results, indent=8))
    trackList = []
    # For each track in the playlist.
    for i in results["items"]:
        # In case there's only one artist.
        if (i["track"]["artists"].__len__() == 1):
            # We add trackName - artist.
            trackList.append(i["track"]["name"] + " - " + i["track"]["artists"][0]["name"])
        # In case there's more than one artist.
        else:
            nameString = ""
            # For each artist in the track.
            for index, b in enumerate(i["track"]["artists"]):
                nameString += (b["name"])
                # If it isn't the last artist.
                if (i["track"]["artists"].__len__() - 1 != index):
                    nameString += ", "
            # Adding the track to the list.
            trackList.append(i["track"]["name"] + " - " + nameString)
        # trackList.append(i['track']['name'])
    print(trackList)
    return trackList

def searchYoutubeAlternative(songName):
    # YouTube will block you if you query too many songs using this search.
    textToSearch = songName
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = bs4.BeautifulSoup(html, 'html.parser')
    for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
        print('https://www.youtube.com' + vid['href'])

def searchYoutube(songName):
    api = youtube.API(client_id=os.getenv("YOUTUBE_CLIENT_ID"),
              client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
              api_key=os.getenv("YOUTUBE_API_KEY"))
    video = api.get('search', q=songName, maxResults=1, type='video', order='relevance')
    try:
        return ("https://www.youtube.com/watch?v="+video["items"][0]["id"]["videoId"])
    except:
        print(songName+' isn\'t available')
        searchYoutubeAlternative(songName)

# if (__name__ == "__main__"):
#     tracks = getTracks(str(input("Insert Spotify playlist URL: ")))
#     print("Searching songs...")
#     songs = []
#     for i in tracks:
#         songs.append(searchYoutube(i))
#     print("Search finished!")

#     print("URL LIST: ")
#     for i in songs:
#         print(i)



list = [0] * 10
for _ in range(1000000):
    list[random.randint(1,10)-1] += 1
print(list)
