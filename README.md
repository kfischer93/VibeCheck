A Discord bot that retrieves music data from Spotify, fetches lyrics from Genius, and performs sentiment analysis on songs using vader.
INFO 3510 Fall 2025

1. Setup 
- Install:
    pip install discord.py
    pip install python-dotenv
    pip install spotipy 
    pip install lyricsgenius 
    pip install nltk matplotlib
- Make sure you have your 3510.env file with your API credentials set up as they are below for me:
    DISCORD_TOKEN=
    SPOTIFY_CLIENT_ID=
    SPOTIFY_CLIENT_SECRET=
    GENIUS_CLIENT_ACCESS_TOKEN=
- Files need to be all in one folder. For example: mine are found in "Music as Info". If you put all these files (and your env file) in a common folder, you can copy the path of it within your jupyter notebook by right clicking the "musicBot.py" file and copying the path to paste into your terminal. Here's what mine looks like when i right click it: "Music as Info/musicBot.py"
- The files needed: 
    musicBot.py - Main bot with command handlers
    spotifyHelper.py - Spotify API functions
    geniusHelper.py - Genius API functions
    vaderHelper.py - Sentiment analysis functions
    3510.env

2. Open discord.

3. Run the bot:
Run "Music as Info" (or name of whatever file you put these all in)
Once you're in that, run "python musicBot.py"
this should wake up the discord bot with a message in your terminal like: 
"1437181052975054868 MAI TAI has connected to Discord." and if your volume is on, you'll hear the little discord bot wake up 

4. Play around! say hi, and the bot will tell you what commands you can use. They're also listed below. thanks for checking it out! :-) 
- Commands you can use:
    /toptracks [artist] - Get top 10 tracks for an artist
    /lyrics [artist] + [song] - Get song lyrics
    /searchlyrics [snippet] - Search for songs by lyrics
    /sentiment [artist] + [song] - Analyze sentiment of lyrics
    /sentimentplot [artist] + [song] - Visualize sentiment progression