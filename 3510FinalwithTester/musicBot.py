import discord # discord python library for interacting with Discord's API
from discord.ext import commands # commands extension, which makes it easier to create bot commands with decorators like @bot.command()
import asyncio # lets the bot handle multiple tasks at once without blocking (like waiting for discord responses)
import os # operating system module that lets us access environment variables
from dotenv import load_dotenv 
import spotifyHelper as shf 
import geniusHelper as ghf 
import vaderHelper as vh 

'''
musicBot.py 

This bot retrieves the top tracks for any artist from Spotify.

Upon firing up the bot, you can say anything in the chat and it will give you a bulleted list of the following commands. 

COMMANDS:

1. /toptracks [artist name]: retrieves top 10 tracks for any artist from spotify sorted by popularity. Each tracks hows the track name, album, and popularity score which was stored as a tuple in a set. example: /toptracks Post Malone would output:
    Top Tracks by Post Malone
    1. Circles - Hollywood's Bleeding (Popularity: 85)
    2. I Had Some Help (Feat. Morgan Wallen) - F-1 Trillion (Popularity: 82)
    3. Sunflower - Spider-Man: Into the Spider-Verse - Hollywood's Bleeding (Popularity: 82)
    4. rockstar (feat. 21 Savage) - beerbongs & bentleys (Popularity: 82)
    5. Fortnight (feat. Post Malone) - THE TORTURED POETS DEPARTMENT (Popularity: 81)
    6. Congratulations - Stoney (Deluxe) (Popularity: 80)
    7. Better Now - beerbongs & bentleys (Popularity: 80)
    8. Take What You Want (feat. Ozzy Osbourne & Travis Scott) - Hollywood's Bleeding (Popularity: 79)
    9. Wow. - Hollywood's Bleeding (Popularity: 78)
    10. Guy For That (Feat. Luke Combs) - F-1 Trillion (Popularity: 76)

and if the artist is spelt wrong or isnt found itll send an error back. 

2. /lyrics [artist name] + [song title]: retrieves lyrics for a specific song. Example: /lyrics Mac Miller + Blue World

3. /searchlyrics [lyric snippet]: searches for songs containing a lyric snippet. Example: /searchlyrics "Jeremy can we talk a minute"

4. /sentiment [artist] + [song title] - Analyze sentiment of song lyrics. Example: /lyrics Mac Miller + Blue World

5. /sentimentplot [artist] + [song title] - Visualize the songs sentiment progression. Example: /sentimentplot Pearl Jam + Black 

'''


# from class bot.py file
# turn on logging 
import logging # pythons logging module
logging.basicConfig(level=logging.INFO) # this is good for debugging so i can see whats going on. 

# from Dr. Zietz's class bot.py file
# load our environment variables
load_dotenv("3510.env") # loads all my keys/tokens from 3510.env 
# get our discord token
discordToken = os.getenv("DISCORD_TOKEN") # gets the Discord bot token from environment variables and stores it in TOKEN variable

# from Dr. Zietz's class bot.py file
# specify bot intents
intents = discord.Intents().all() # gives discord permission for bot to access everything (all)

# from Dr. Zietz's class bot.py file
# bot object instantiated from discord module
bot = commands.Bot(command_prefix="/", intents=intents) # creates the bot and tells it a command starts with a "/" and passes the permissions we just set up above ^^




# from Dr. Zietz's class bot.py file
@bot.event # this is a decorator that tells discord that the following function responds to a specific event 
async def on_ready(): # this function is asynchronous (can handle multiple things at once!!)
    channel = discord.utils.get(bot.get_all_channels(), name="general") # gets every channel the bot can see in every server and looks for one named "general"
    if channel: # check to make sure the channel exists, if you try to send a message to None, bot will crash
        await channel.send("Music bot is online!") # await means "wait for this to finish before continuing"
    print(f"{bot.user.id} {bot.user.name} has connected to Discord.") # prints to the terminal (not discord) confirming the bot connected

# all bot code needs to come before asyncio.run




# Event: respond to messages
# adapted from class bot.py file
@bot.event # decorator that registers this as an event handler
async def on_message(message): # runs everytime ANY message is sent in the channel 
    # Ignore messages from the bot itself so that we dont end up in an infinate loop
    if message.author == bot.user: # checks if the bot sent the message
        await bot.process_commands(message)
        return # exits the function early 
    
    if message.content.startswith("/"):
        # If it IS a command, just process it
        await bot.process_commands(message)
    else:
        # If it's NOT a command, send the help message
        await message.channel.send(
            "Want to learn about some music?\n\n"
            "1. /toptracks [artist name] - Get top 10 tracks for any artist\n"
            "2. /lyrics [artist] + [song title] - Get lyrics for a specific song\n"
            "3. /searchlyrics [lyric snippet] - Search for songs by lyrics\n"
            "4. /sentiment [artist] + [song title] - Analyze sentiment of song lyrics\n"
            "5. /sentimentplot [artist] + [song title] - Visualize sentiment throughout song\n"
            "6. /sayhello [names] - Say hello to the bot!\n\n"
        )    



# command: get top tracks for an artist from spotify using spotifyHelper.py file functions 
# modified from Dr. Zietz's class bot.py file
@bot.command() # decorator that registers this as a bot command (no brief or description needed since we made our own help menu)
async def toptracks(ctx, *args): # ctx is context object with info about who sent the command, *args captures ALL words after /toptracks as a tuple. the * allows for it to be more than one argument or one word 
    # Join the artist name
    artistName = " ".join(args) # join the artist name... turns ('Mac', 'Miller') into "Mac Miller"
    
    # Get the track data (just a set of tuples!) call my helper function to get track data from Spotify
    #A tuple is like a list, but immutable (can't be changed after its created)
    result = shf.getTopTracks(artistName) # calls the getTopTracks function from spotifyHelper.py
    
    # check if artist was found... if not, send error message and exit
    if result is None: # if the function returned None, that means the artist wasn't found
        await ctx.send(f"Could not find artist: {artistName}") # sends error message to discord
        return # exits the function early so we don't try to process None

    # unpack the result into two variables: the track data set and the proper artist name
    trackData, artistActualName = result # unpacks the tuple returned by getTopTracks into two separate variables
    
    # the message we build to return to the user, and two new lines 
    message = f"Top Tracks by {artistActualName}\n\n" # starts building the message string with the artist name

    # sort the tracks by popularity. key=lambda x: x[2] means sort by the 3rd item in each tuple (popularity score)
    # reverse=True means highest popularity first
    sortedTracks = sorted(trackData, key=lambda x: x[2], reverse=True) # lambda function says "for each item x, look at x[2]" and in this case we are sorting the tracks by x[2] which is popularity score! the reverse True makes the highest scores go first (most popularrrr) 
    
    # enumerate gives us a counter starting at 1, and unpacks each tuple into trackName, albumName, and popularity
    for i, (trackName, albumName, popularity) in enumerate(sortedTracks, 1): # enumerate gives us both the index (starting at 1), and the tuple
        message += f"{i}. {trackName} - {albumName} (Popularity: {popularity})\n" # adds each track to the message with formatting
        # for example ^^: 
        # message += f"{i}. {trackName} - {albumName} (Popularity: {popularity})\n"
        # message += f"{1}. {Circles} - {Hollywood's Bleeding} (Popularity: {85})\n"
        # message += "1. Circles - Hollywood's Bleeding (Popularity: 85)\n"
    await ctx.send(message) # sends the complete message to discord





# command: get lyrics for a specific song using geniusHelper.py file functions
@bot.command() # decorator that registers this as a bot command
async def lyrics(ctx, *args): # *args captures all words after /lyrics
    # Join all arguments into one string
    fullInput = " ".join(args) # combines all the words into one string so we can search for the "+" separator
    
    # Check if there's a separator. need the separator otherwise where does teh artist name start and song begin?
    if "+" not in fullInput: # checks if the user included the "+" separator we need
        await ctx.send("Please use format: /lyrics [artist] + [song title]\nExample: /lyrics Post Malone + Circles") # sends error message with example
        return # exits early
    
    # Split by the + separator
    parts = fullInput.split("+") # splits the string at the "+" into a list with 2 items
    artistName = parts[0].strip() # takes the first part (artist name) and .strip() removes extra spaces
    songTitle = parts[1].strip() # takes the second part (song title) and removes extra spaces
    
    await ctx.send(f"Searching for lyrics to '{songTitle}' by {artistName}...") # sends a "processing" message to let user know bot is working
    
    lyrics = ghf.getLyrics(artistName, songTitle) # calls the getLyrics function from geniusHelper.py
    
    if lyrics: # checks if lyrics were found (lyrics will be None if not found)
        for page in ghf.discordMessageSlicer(lyrics): # splits lyrics into chunks under 2000 characters since discord has a limit
            await ctx.send(page) # sends each chunk as a separate message
    else: # if no lyrics were found
        await ctx.send(f" Could not find lyrics for '{songTitle}' by {artistName}. Try checking the spelling!") # sends error message





# command: search for songs by a lyric snippet using geniusHelper.py file functions
@bot.command() # decorator that registers this as a bot command
async def searchlyrics(ctx, *args): # *args captures the lyric snippet the user wants to search for
    # Join all the words into the lyric snippet
    lyricSnippet = " ".join(args) # combines all words into one string
    
    if not lyricSnippet: # checks if the string is empty (user didn't provide any lyrics)
        await ctx.send("Please provide a lyric snippet to search for. Example: /searchlyrics Jeremy can we talk a minute") # sends error message
        return # exits early
    
    # Send a "processing" message
    await ctx.send(f"Searching for songs with lyrics: '{lyricSnippet}'...") # lets user know the bot is working on it
    
    # Search for songs using our helper function
    results = ghf.searchByLyrics(lyricSnippet, maxResults=5) # calls the searchByLyrics function, asks for max 5 results
    
    # Check if we found any songs
    if results: # checks if any songs were found (results will be None if nothing found)
        # Build the message to send back
        message = f"Found {len(results)} song with those lyrics:\n\n" # len(results) gives us the number of songs found
        
        # Loop through results and add them to the message
        for i, (songTitle, artistName) in enumerate(results, 1): # enumerate gives us counter starting at 1, unpacks each tuple
            message += f"{i}. {songTitle} by {artistName}\n" # adds formatted line for each song. f strings vs. old string concatenation 
        
        message += f"\nUse /lyrics [artist] [song title] to see full lyrics!" # adds helpful tip at the end
        
        await ctx.send(message) # sends the complete message
    else: # if no songs were found
        await ctx.send(f"Could not find any songs with the lyrics: '{lyricSnippet}'. Try different words!") # sends error message





# command: analyze sentiment of a song's lyrics
@bot.command() # decorator that registers this as a bot command
async def sentiment(ctx, *args): # *args captures all words after /sentiment
    # Join all arguments into one string
    fullInput = " ".join(args) # combines all words into one string so we can look for the "+" separator
    
    # Check if there's a separator
    if "+" not in fullInput: # checks if user included the "+" we need to separate artist and song
        await ctx.send("Please use format: /sentiment [artist] + [song title]\nExample: /sentiment Mac Miller + Good News") # error message with example
        return # exits early
    
    # split by the + separator
    parts = fullInput.split("+") # splits string at "+" into a list
    artistName = parts[0].strip() # gets first part (the artist) and strip removes extra spaces
    songTitle = parts[1].strip() # gets second part (the song) and strip removes extra spaces
    
    # Send a processing message
    await ctx.send(f"Analyzing sentiment for '{songTitle}' by {artistName}...") # lets user know bot is working
    
    # Get the lyrics from Genius
    lyrics = ghf.getLyrics(artistName, songTitle) # calls getLyrics function to get the song lyrics
    
    if not lyrics: # checks if lyrics is None (not found)
        await ctx.send(f"Could not find lyrics for '{songTitle}' by {artistName}. Try checking the spelling!") # error message
        return # exits early
    
    # Analyze the sentiment using VADER
    sentimentResults = vh.analyzeLyrics(lyrics) # calls analyzeLyrics function which uses VADER to analyze sentiment
    
    if not sentimentResults: # checks if analysis failed
        await ctx.send("Could not analyze sentiment for this song.") # error message
        return # exits early
    
    # Format and send the results
    formattedResults = vh.formatSentimentResults(sentimentResults) # calls function to format results into readable text
    await ctx.send(formattedResults) # sends the formatted sentiment analysis





# command: create sentiment visualization
@bot.command() # decorator that registers this as a bot command
async def sentimentplot(ctx, *args): # *args captures all words after /sentimentplot
    # Join all arguments into one string
    fullInput = " ".join(args) # combines all words into one string
    
    # Check if there's a separator
    if "+" not in fullInput: # checks if user included the "+" separator
        await ctx.send("Please use format: /sentimentplot [artist] + [song title]\nExample: /sentimentplot Mac Miller + Good News") # error with example
        return # exits early
    
    # Split by the + separator
    parts = fullInput.split("+") # splits at "+" into a list
    artistName = parts[0].strip() # gets artist name and removes spaces
    songTitle = parts[1].strip() # gets song title and removes spaces
    
    # Send a processing message
    await ctx.send(f"Creating sentiment visualization for '{songTitle}' by {artistName}...") # lets user know bot is creating the plot
    
    # Get the lyrics from Genius
    lyrics = ghf.getLyrics(artistName, songTitle) # gets the lyrics
    
    if not lyrics: # checks if lyrics weren't found
        await ctx.send(f"Could not find lyrics for '{songTitle}' by {artistName}. Try checking the spelling!") # error message
        return # exits early
    
    # Analyze the sentiment using VADER
    sentimentResults = vh.analyzeLyrics(lyrics) # analyzes sentiment using VADER
    
    if not sentimentResults: # checks if analysis failed
        await ctx.send("Could not analyze sentiment for this song.") # error message
        return # exits early
    
    # Create the visualization
    savedVisualizationFilename = vh.sentimentViz(sentimentResults, artistName, songTitle) # creates the plot and saves it as a PNG, returns the filename
    
    if not savedVisualizationFilename: # checks if visualization creation failed
        await ctx.send("Could not create visualization.") # error message
        return # exits early
    
    # create a file object to send to Discord
    visualizationFileObject = discord.File(savedVisualizationFilename, filename=savedVisualizationFilename) # creates a Discord file object from the saved PNG
    
    # Send the file to Discord
    await ctx.send(f"Sentiment progression for '{songTitle}' by {artistName}:", file=visualizationFileObject) # sends message with the image file attached




# from Dr. Zietz's class bot.py file
# you have to tell the bot to actually run
asyncio.run(bot.start(discordToken)) # bot.start() starts the bot using my discord token, asyncio.run() runs it asynchronously
# bot objects have a start method that start up the bot
# TOKEN authenticates your bot
# asyncio is running whatever you pass it asynchronously