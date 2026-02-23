import os # operating system module for accessing environment variables
from dotenv import load_dotenv # loads environment variables from .env file
import spotipy # spotipy library makes Spotify API easier to use
from spotipy.oauth2 import SpotifyClientCredentials # imports the authentication we neeed for spotify 
load_dotenv("3510.env") # loads our Spotify credentials from the 3510.env file

# create the authentication manager using our Spotify client ID and secret from the .env file
clientCredentialManager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"), # gets the client ID from environment variables
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET") # gets the client secret from environment variables
)

# create the Spotify API client object that we'll use to make all our Spotify requests
sp = spotipy.Spotify(client_credentials_manager=clientCredentialManager) # this sp object lets us search artists, get tracks, etc.

'''
spotifyHelper.py

This file contains helper functions for interacting with the Spotify API to retrieve 
artist and track information.

Uses the Spotipy library to simplify Spotify API calls.
Spotipy documentation: https://spotipy.readthedocs.io/
'''

# make a function to get the top 10 songs from an artist. 
def getTopTracks(artistName): # defines a function that takes an artist name as input
    # get the top tracks for a given artist name
    # returns a set of tuples containing the track name, album name, and the popularity
    # search for the artist
    results = sp.search(q=artistName, type='artist', limit=1) # searches Spotify for the artist, q is the query, type='artist' means only search for artists not songs, limit=1 returns only the best match
    
    # now check if the artist was found
    if not results['artists']['items']: # results['artists']['items'] is a list, if it's empty that means no artist was found
        return None # returns None so we can check for this error in the main bot file
    
    # this is how we get the artist id which is needed to ask for the top 10 songs, and since its a bot
    # having this in the function is necessary since i dont just have a database of all artists ID somewhere. 
    # we have to find a way to search for it and how i did that in project 1 as well as in class notes is we have to 
    # sift through the disctionary to get the ID since the only other way is to manually go to the artist's spotify
    # url and grab it from the end but idk how to do that and this works so here we go
    artistID = results['artists']['items'][0]['id'] # navigates through the nested dictionary: results is a dict, ['artists'] gets the artists section, ['items'] gets the list of artists, [0] gets the first artist, ['id'] gets their unique Spotify ID
    artistActualName = results['artists']['items'][0]['name'] # this is so that it gives us the spotify name, which is cleaner than
    # a name just written in whatever way like "macmiller" or "MACMILLER" or "mac Miller"... it just returns whatever name is in that 
    # spotify artists dictionary, ideally "Mac Miller"
    # Get top tracks
    # this literally just takes the ID we just got and named "artistID" and fetches the top 10 songs which is what spotify
    # artist_top_tracks does. we dont need to specify anywhere for only 10 becuase this only gives us the top 10. 
    topTracks = sp.artist_top_tracks(artistID, country='US') # calls the Spotify API method to get top tracks for this artist ID, US so it gives us US popularity rankings
    tracks = topTracks['tracks'] # and here we are naming the top tracks that we retrieved as tracks to give us just the tracks list from the response dictionary
    
    # create set to store track data which will contain tuples... this is just like in Dr. Zietz's reverb helper functions py file 
    setOfTrackData = set() # creates an empty set to store our track information, sets automatically remove duplicates
    
    # Now we are looping through each track in the tracks list and for each track, we are taking out the track name, album name, 
    # and the popularity and bundling those things into a tuple. 
    for track in tracks: # loops through each track in the tracks list (up to 10 tracks)
        trackName = track['name'] # extracts the track name from the track dictionary
        albumName = track['album']['name'] # navigates through track dictionary to get album name (track['album'] is another dict, then ['name'] gets the album name)
        popularity = track['popularity'] # extracts the popularity score (0-100)
        
        trackDataTuple = (trackName, albumName, popularity) # here is the tuple we will be bundling up and storing in the setOfTrackData set, parentheses create a tuple
        setOfTrackData.add(trackDataTuple) # here is where we add it, .add() is the method for adding items to a set
    
    return setOfTrackData, artistActualName # returns two things: the set of track data and the artist actual name that we got earlier in the code, this is called tuple unpacking