import os
from dotenv import load_dotenv
from lyricsgenius import Genius

load_dotenv("3510.env")

genius = Genius(os.getenv("GENIUS_CLIENT_ACCESS_TOKEN"))

genius.excluded_terms = ["(Remix)", "(Live)"]
genius.remove_section_headers = True


def getLyrics(artistName, songTitle):
    song = genius.search_song(songTitle, artistName)
    
    if song:
        return song.lyrics
    else:
        return None


def searchByLyrics(lyricSnippet, maxResults=5):
    request = genius.search_lyrics(lyricSnippet)
    
    if not request:
        return None
    
    songs = []
    
    for hit in request['sections'][0]['hits'][:maxResults]:
        title = hit['result']['title']
        artist = hit['result']['primary_artist']['name']
        songs.append((title, artist))
    
    if songs:
        return songs
    else:
        return None


def discordMessageSlicer(message):
    pageSizeLimit = 2000
    
    if type(message) != str:
        print("discordMessageSlicer can only paginate strings")
        return None
    
    messagePieces = []
    
    for i in range(0, 1 + len(message) // pageSizeLimit):
        if len(message) < i * pageSizeLimit + pageSizeLimit:
            currentPiece = message[i * pageSizeLimit:]
        else:
            currentPiece = message[i * pageSizeLimit:(i * pageSizeLimit) + pageSizeLimit]
        
        messagePieces.append(currentPiece)
    
    return messagePieces
