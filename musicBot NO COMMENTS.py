import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv 
import spotifyHelper as shf 
import geniusHelper as ghf 
import vaderHelper as vh 

import logging
logging.basicConfig(level=logging.INFO)

load_dotenv("3510.env")
discordToken = os.getenv("DISCORD_TOKEN")

intents = discord.Intents().all()

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    channel = discord.utils.get(bot.get_all_channels(), name="general")
    if channel:
        await channel.send("Music bot is online!")
    print(f"{bot.user.id} {bot.user.name} has connected to Discord.")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        await bot.process_commands(message)
        return
    
    if message.content.startswith("/"):
        await bot.process_commands(message)
    else:
        await message.channel.send(
            "Want to learn about some music?\n\n"
            "1. /toptracks [artist name] - Get top 10 tracks for any artist\n"
            "2. /lyrics [artist] + [song title] - Get lyrics for a specific song\n"
            "3. /searchlyrics [lyric snippet] - Search for songs by lyrics\n"
            "4. /sentiment [artist] + [song title] - Analyze sentiment of song lyrics\n"
            "5. /sentimentplot [artist] + [song title] - Visualize sentiment throughout song\n"
            "6. /sayhello [names] - Say hello to the bot!\n\n"
        )


@bot.command()
async def toptracks(ctx, *args):
    artistName = " ".join(args)
    
    result = shf.getTopTracks(artistName)
    
    if result is None:
        await ctx.send(f"Could not find artist: {artistName}")
        return

    trackData, artistActualName = result
    
    message = f"Top Tracks by {artistActualName}\n\n"

    sortedTracks = sorted(trackData, key=lambda x: x[2], reverse=True)
    
    for i, (trackName, albumName, popularity) in enumerate(sortedTracks, 1):
        message += f"{i}. {trackName} - {albumName} (Popularity: {popularity})\n"
    await ctx.send(message)


@bot.command()
async def lyrics(ctx, *args):
    fullInput = " ".join(args)
    
    if "+" not in fullInput:
        await ctx.send("Please use format: /lyrics [artist] + [song title]\nExample: /lyrics Mac Miller + Blue World")
        return
    
    parts = fullInput.split("+")
    artistName = parts[0].strip()
    songTitle = parts[1].strip()
    
    await ctx.send(f"Searching for lyrics to '{songTitle}' by {artistName}...")
    
    lyrics = ghf.getLyrics(artistName, songTitle)
    
    if lyrics:
        for page in ghf.discordMessageSlicer(lyrics):
            await ctx.send(page)
    else:
        await ctx.send(f" Could not find lyrics for '{songTitle}' by {artistName}. Try checking the spelling!")


@bot.command()
async def searchlyrics(ctx, *args):
    lyricSnippet = " ".join(args)
    
    if not lyricSnippet:
        await ctx.send("Please provide a lyric snippet to search for. Example: /searchlyrics Jeremy can we talk a minute")
        return
    
    await ctx.send(f"Searching for songs with lyrics: '{lyricSnippet}'...")
    
    results = ghf.searchByLyrics(lyricSnippet, maxResults=5)
    
    if results:
        message = f"Found {len(results)} song with those lyrics:\n\n"
        
        for i, (songTitle, artistName) in enumerate(results, 1):
            message += f"{i}. {songTitle} by {artistName}\n"
        
        message += f"\nUse /lyrics [artist] [song title] to see full lyrics!"
        
        await ctx.send(message)
    else:
        await ctx.send(f"Could not find any songs with the lyrics: '{lyricSnippet}'. Try different words!")


@bot.command()
async def sentiment(ctx, *args):
    fullInput = " ".join(args)
    
    if "+" not in fullInput:
        await ctx.send("Please use format: /sentiment [artist] + [song title]\nExample: /sentiment Mac Miller + Good News")
        return
    
    parts = fullInput.split("+")
    artistName = parts[0].strip()
    songTitle = parts[1].strip()
    
    await ctx.send(f"Analyzing sentiment for '{songTitle}' by {artistName}...")
    
    lyrics = ghf.getLyrics(artistName, songTitle)
    
    if not lyrics:
        await ctx.send(f"Could not find lyrics for '{songTitle}' by {artistName}. Try checking the spelling!")
        return
    
    sentimentResults = vh.analyzeLyrics(lyrics)
    
    if not sentimentResults:
        await ctx.send("Could not analyze sentiment for this song.")
        return
    
    formattedResults = vh.formatSentimentResults(sentimentResults)
    await ctx.send(formattedResults)


@bot.command()
async def sentimentplot(ctx, *args):
    fullInput = " ".join(args)
    
    if "+" not in fullInput:
        await ctx.send("Please use format: /sentimentplot [artist] + [song title]\nExample: /sentimentplot Mac Miller + Good News")
        return
    
    parts = fullInput.split("+")
    artistName = parts[0].strip()
    songTitle = parts[1].strip()
    
    await ctx.send(f"Creating sentiment visualization for '{songTitle}' by {artistName}...")
    
    lyrics = ghf.getLyrics(artistName, songTitle)
    
    if not lyrics:
        await ctx.send(f"Could not find lyrics for '{songTitle}' by {artistName}. Try checking the spelling!")
        return
    
    sentimentResults = vh.analyzeLyrics(lyrics)
    
    if not sentimentResults:
        await ctx.send("Could not analyze sentiment for this song.")
        return
    
    savedVisualizationFilename = vh.sentimentViz(sentimentResults, artistName, songTitle)
    
    if not savedVisualizationFilename:
        await ctx.send("Could not create visualization.")
        return
    
    visualizationFileObject = discord.File(savedVisualizationFilename, filename=savedVisualizationFilename)
    
    await ctx.send(f"Sentiment progression for '{songTitle}' by {artistName}:", file=visualizationFileObject)


asyncio.run(bot.start(discordToken))
