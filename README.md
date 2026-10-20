# KookiesBot

A Discord bot I wrote in Python with discord.py between 2020 and 2022. It plays music, tracks XP and levels, runs moderation tools and reaction roles, and has a set of fun and utility commands.

## How it works

**Startup.** `Kookies-bot.py` creates a `commands.Bot` that answers to the `;` prefix or a mention, then loads each feature from `cogs/` as its own extension (a cog). The loaded cogs are `CommandErrorHandler`, `helpmenu`, `levels`, `mainmusic`, `fun`, `moderation`, `roles`, `server`, `misc`, `utility`, `deten` and `jisha`. The other files in `cogs/` (`level`, `xp`, `exp`, `musiclava`, `musicworking`, `music copy`, `testm`, `games`, `slash`, `school`) are earlier versions or experiments that are no longer loaded, and `Backups/` holds older copies of the whole bot.

**Every message.** A global check reads `blacklist.json` and refuses commands from blacklisted users. `on_message` runs the command, and in servers that turned on pruning (`;prune`, saved in `config.json`) it waits the set number of seconds and then deletes both the `;` message and the bot's reply so channels stay clean.

**Errors and cooldowns.** `CommandErrorHandler` catches failed commands and turns common errors (unknown command, missing permissions, cooldowns, bad arguments) into short replies. Most commands share a per-user cooldown read from `config.json`.

**Help menu.** `helpmenu` lists every command's short description and usage, grouped by cog, as pages you flip through with reactions (discord-ext-menus).

**XP and levels (`cogs/levels.py`).** A message earns a random 15 to 25 XP, at most once every 60 seconds per user (the last-message times live in `cooldown.json`). XP is stored in MongoDB with one collection per server, and the level is computed from XP as `int(((12 * xp) // 800) ** 0.55)`. `;rank` shows a member's XP, level and rank, and `;leaderboard` recomputes everyone's rank and pages through the list.

**Music (`cogs/mainmusic.py`).** Audio is streamed by a separate Lavalink server (a Java audio node; `cogs/application.yml` is its config). The bot connects to it with lavalink.py. When you `;play` something:

1. A plain search becomes `ytsearch:<query>`, or `scsearch:<query>` for `;scplay` (SoundCloud), and Lavalink returns matching tracks.
2. A Spotify playlist link is expanded with spotipy into one search string per song (the first 100 songs, since it reads only one page). Each one is searched on YouTube, and if nothing comes back the bot swaps the two halves of the string and tries again.
3. Tracks go into a per-server queue with skip, skipto, seek, shuffle, loop, remove and volume commands. `;equalizer` applies preset gain bands (such as bass boost), and `;save` DMs you the song that's playing.

**Moderation (`cogs/moderation.py`, `cogs/deten.py`).** `;mute` creates a `Muted` role if the server doesn't have one (hidden from every channel), swaps the member's roles for it, and saves the old roles to MongoDB so `;unmute` can give them back. It can also lift the mute after a set number of minutes. Detention works the same way with a `Detention` role, except the member gets one channel, #detention, where they have to type a given phrase a set number of times. `deten.py` watches that channel, counts the correct messages, and gives the saved roles back once the count is reached. Other commands cover bans, kicks, locking channels or the whole server, slowmode, bulk delete and the blacklist.

**Reaction roles (`cogs/roles.py`).** `;roleclaim @role1 @role2 ...` (up to 10 roles) posts a message with a numbered emoji for each role and stores the message's roles in MongoDB. The raw reaction listeners look that message up and add or remove the matching role when someone reacts or removes their reaction.

**Server tools (`cogs/server.py`).** Join and leave messages (the channel is set with `;welcome` and saved in `guild.json`), commands to create and edit channels and categories, and the prune setting above.

**Fun and utility.** Word lookups (Urban Dictionary and WordNet through NLTK), rhymes and advice from public APIs, server and user info, `;repeat` and `;snipe` (which shows who last used `;repeat`), an 8-ball and a few joke commands. `jishaku` adds an owner-only debug console.

## Running it

It was written for Python 3.8 (`runtime.txt`) and the discord.py 2.0 development branch, and was hosted as a Heroku worker (`Procfile`). It hasn't been updated since 2022, so newer library versions may need changes.

1. `pip install -r requirements.txt`
2. Start a Lavalink server, using `cogs/application.yml` as its config.
3. Set these environment variables:
   - `MONGO_URI`: database for moderation, detention, reaction roles and music
   - `MONGO_URI_2`: database for XP and levels, and the owner-only voice-channel time counter (`;vct`)
   - `LAVALINK_HOST`, `LAVALINK_PORT`, `LAVALINK_PASSWORD`: the Lavalink server from step 2
   - `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`: for expanding Spotify playlists
   - Optional: `KSOFT_API_KEY` and `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` are still read by a few cogs, but the commands that used them are commented out
4. Replace `'token here'` in `main()` in `Kookies-bot.py` with your bot token, then run `python Kookies-bot.py`.

## Known issues

- The level-up message rarely fires: the "level before this gain" line in `cogs/levels.py` subtracts the new XP before multiplying by 12 instead of after.
- When the music queue ends, the event hook in `cogs/mainmusic.py` uses `channel` before it is set, so the bot stays in voice until `;leave`.
