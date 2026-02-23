'''
geniusHelper.py

This helper file contains helper functions for interacting with the Genius API to retrieve song lyrics
and search for songs. 

* Documentation and code snippets have been adapted from:
* https://lyricsgenius.readthedocs.io/en/master/examples/snippets.html
'''

import os # operating system module for accessing environment variables
from dotenv import load_dotenv # loads environment variables from .env file
from lyricsgenius import Genius # imports the LyricsGenius library which is a wrapper for the Genius API

# load up the 3510.env file, has all my access tokens etc
load_dotenv("3510.env") # loads our Genius access token from the 3510.env file

# initialize Genius API client with access token
genius = Genius(os.getenv("GENIUS_CLIENT_ACCESS_TOKEN")) # creates the Genius API client object using our access token 

# exclude remixes and live versions from search results
# this helps clean up results and get original versions
# snippet from: https://lyricsgenius.readthedocs.io/en/master/examples/snippets.html#searching-for-a-song-by-lyrics
genius.excluded_terms = ["(Remix)", "(Live)"] # tells Genius to skip songs with these terms in the title, so we get original versions

# remove section headers like [Chorus], [Verse 1], etc. from lyrics
# makes the lyrics cleaner for sentiment analysis
genius.remove_section_headers = True # removes the [Chorus], [Verse 1] tags from lyrics to make them cleaner for analysis


def getLyrics(artistName, songTitle): # defines function that takes artist name and song title as inputs
    '''
    we will get lyrics for a specific song by artist name and song title.
    
    * this uses the Genius.search_song() method to find and retrieve lyrics.
    * this is documented at: https://lyricsgenius.readthedocs.io/en/master/examples/snippets.html#searching-for-a-song
    
    args:
        artistName (str): The name of the artist
        songTitle (str): The title of the song
    
    returns:
        str: the lyrics as a string, or None if the song is not found or an error comes up
    
    Example:
        lyrics = getLyrics("Mac Miller", "Blue World")
    '''
   
    song = genius.search_song(songTitle, artistName) # searches Genius for the song, returns a song object or None if not found
    
    if song: # checks if a song was found (song will be None if not found)
        return song.lyrics # returns the lyrics as a string from the song object
    else: # if no song was found
        return None # returns None so we can handle this error in the main bot file



def searchByLyrics(lyricSnippet, maxResults=5): # defines function that takes a lyric snippet and optional max results (default is 5)
    '''
    Search for songs by a snippet of lyrics.
    
    Uses the Genius.search_lyrics() method to find songs containing the lyric snippet.
    Method documented at: https://lyricsgenius.readthedocs.io/en/master/examples/snippets.html#searching-for-a-song-by-lyrics
    
    args:
        lyricSnippet (str): A snippet of lyrics to search for (e.g., "Jeremy can we talk a minute?")
        maxResults (int): Maximum number of results to return (default: 5)
    
    returns:
        list: A list of tuples containing (song_title, artist_name), or None if no results found
    
    example:
        results = searchByLyrics("Jeremy can we talk a minute?")
        if results:
            for title, artist in results:
                print(f"{title} by {artist}")
        else:
            print("No songs found with those lyrics")
    '''
    # From documentation: https://lyricsgenius.readthedocs.io/en/master/examples/snippets.html#searching-for-a-song-by-lyrics
    # Example usage:
    # request = genius.search_lyrics('Jeremy can we talk a minute?')
    # for hit in request['sections'][0]['hits']:
    #     print(hit['result']['title'])
    
    request = genius.search_lyrics(lyricSnippet) # searches Genius for songs containing the lyric snippet, returns a complex nested dictionary
    
    # Check if we got anything back
    if not request: # checks if request is None or empty (search failed)
        return None # returns None to indicate no results
    
    songs = [] # creates empty list to store the song results
    
    # Loop through results (if the structure is wrong, this will just fail and we return None)
    for hit in request['sections'][0]['hits'][:maxResults]: # navigates to the hits list in the response, [:maxResults] slices to only get first 5 results
        title = hit['result']['title'] # extracts the song title from the nested dictionary
        artist = hit['result']['primary_artist']['name'] # navigates through the dict to get the artist name
        songs.append((title, artist)) # creates a tuple with title and artist, adds it to the songs list
    
    # Return songs if we found any, otherwise None
    if songs: # checks if the songs list has any items in it
        return songs # returns the list of tuples
    else: # if the list is empty
        return None # returns None to indicate no results found



def discordMessageSlicer(message): # defines function that takes a message string and splits it into chunks
    '''
    Split long messages into chunks that fit Discord's 2000 character limit.
    
    This function is copied from spotifyHelper.py via Dr. Zietz's bot.py file from class practice in order
    to stay consistent within the helper files. I was going to do it in all helper files, till i realized that
    the only helper file that will really be dealing with long character messages would be this one as its 
    dealing with lyrics which can run long.
    Discord has a strict 2000 character limit per message, so longer content (like full lyrics)
    needs to be split into multiple messages.
    
    args:
        message (str): The message to split
    
    returns:
        list: A list of message chunks, each under 2000 characters, or None if input is not a string
    
    example:
        lyrics = getLyrics("Mac Miller", "Blue World")
        for chunk in discordMessageSlicer(lyrics):
            await ctx.send(chunk)
    '''
    pageSizeLimit = 2000 # Discord's character limit per message
    
    # Validate input is a string
    if type(message) != str: # checks if the input is a string
        print("discordMessageSlicer can only paginate strings") # prints error message to terminal
        return None # returns None to indicate error
    
    messagePieces = [] # creates empty list to store the message chunks
    
    # Calculate number of chunks needed
    # If message is 6000 chars: 6000//2000 = 3 full chunks
    for i in range(0, 1 + len(message) // pageSizeLimit): # calculates how many chunks we need, // is integer division, +1 accounts for partial chunks
        # Check if this is the last chunk
        if len(message) < i * pageSizeLimit + pageSizeLimit: # checks if the remaining message is shorter than 2000 characters (last chunk)
            # Last chunk: take everything from current position to end
            currentPiece = message[i * pageSizeLimit:] # string slicing that takes from current position to the end
        else: # if not the last chunk
            # Not last chunk: take exactly 2000 characters
            currentPiece = message[i * pageSizeLimit:(i * pageSizeLimit) + pageSizeLimit] # takes exactly 2000 characters using string slicing
        
        messagePieces.append(currentPiece) # adds the chunk to our list
    
    return messagePieces # returns the list of chunks, each under 2000 characters