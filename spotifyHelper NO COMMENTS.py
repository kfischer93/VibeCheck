import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv("3510.env")

clientCredentialManager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
)

sp = spotipy.Spotify(client_credentials_manager=clientCredentialManager)


def getTopTracks(artistName):
    results = sp.search(q=artistName, type='artist', limit=1)
    
    if not results['artists']['items']:
        return None
    
    artistID = results['artists']['items'][0]['id']
    artistActualName = results['artists']['items'][0]['name']
    
    topTracks = sp.artist_top_tracks(artistID, country='US')
    tracks = topTracks['tracks']
    
    setOfTrackData = set()
    
    for track in tracks:
        trackName = track['name']
        albumName = track['album']['name']
        popularity = track['popularity']
        
        trackDataTuple = (trackName, albumName, popularity)
        setOfTrackData.add(trackDataTuple)
    
    return setOfTrackData, artistActualName
