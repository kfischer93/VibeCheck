'''
This file contains helper functions for doing sentiment analysis on song lyrics
using vader.

vader is specifically designed for social media text and works OKAY with song lyrics.
Documentation: https://github.com/cjhutto/vaderSentiment

in spirit of doing the sentiment line by line for a slightly more accurate read instead of 
all at once, I have grouped the song up into 10 words per chunk and will be doing sentiment based on each 10 word chunk.

*** Visualization function at bottom uses claude ai support & the full chat conversation is linked in the dostring 
descrption of the function ***
'''

import nltk # natural language toolkit, an NLP library for text processing
from nltk.sentiment.vader import SentimentIntensityAnalyzer # imports the vader sentiment analyzer from nltk
import matplotlib.pyplot as plt # for creating plots and visualizations

# Download vader lexicon (only needs to happen once, but safe to run multiple times)
nltk.download("vader_lexicon", quiet=True) # downloads the vader dictionary of words and their sentiment scores, quiet=True suppresses the download messages

# Initialize the vader sentiment analyzer
vaderSIA = SentimentIntensityAnalyzer() # creates the sentiment analyzer object that we'll use to analyze text




def analyzeLyrics(lyrics, chunkSize=10): # defines function that takes lyrics and optional chunk size which ive set to 10
    '''
    analyze sentiment of lyrics in chunks of words.
    this shows how sentiment possibly changes throughout different parts of the song.
    
    args:
        lyrics (str): The song lyrics to analyze
        chunkSize (int): Number of words per chunk (10)
    
    returns:
        dict: dictionary containing:
            - 'chunkScores': list of dictionaries with sentiment scores for each chunk
            - 'chunks': list of text chunks
            - 'averageCompound': average compound score across all chunks
        Returns None if lyrics is None or empty
    '''
    # Check if lyrics exist
    if not lyrics: # checks if lyrics is None or empty string
        return None # returns None so we can handle this error in the main bot file
    
    # split lyrics into words
    words = lyrics.split() # splits the lyrics string into a list of words using spaces as the delimiter
    
    # if there are fewer words than chunk size, just analyze the whole thing
    if len(words) <= chunkSize: # if the song has 10 or fewer words, no need to chunk it
        overallScores = vaderSIA.polarity_scores(lyrics) # analyzes the entire lyrics at once, returns a dict with neg, neu, pos, and compound scores
        return { # returns a dictionary with the results
            'chunkScores': [overallScores], # puts the single score in a list for consistency with the multi-chunk format
            'chunks': [lyrics], # puts the entire lyrics in a list
            'averageCompound': overallScores['compound'] # the compound score is already the overall score since there's only one chunk
        }
    
    # initialize lists to store chunk data
    chunkScores = [] # creates empty list to store sentiment scores for each chunk
    chunks = [] # creates empty list to store the actual text of each chunk
    
    # break lyrics into chunks
    for i in range(0, len(words), chunkSize): # loops through words in steps of 10, so i=0, 10, 20, 30, etc.
        # Get the next chunk of words
        chunk = " ".join(words[i:i + chunkSize]) # takes a slice of 10 words starting at position i and joins them back into a string
        
        # get sentiment scores for this chunk
        scores = vaderSIA.polarity_scores(chunk) # analyzes sentiment of this 10 word chunk, returns dict like {'neg': 0.0, 'neu': 0.5, 'pos': 0.5, 'compound': 0.4}
        
        # store the chunk and its scores
        chunks.append(chunk) # adds the chunk text to our chunks list
        chunkScores.append(scores) # adds the sentiment scores to our chunkScores list
    
    # calculate average compound score across all chunks
    compoundScores = [score['compound'] for score in chunkScores] # list comprehension that extracts just the compound score from each chunk's score dictionary
    averageCompound = sum(compoundScores) / len(compoundScores) # calculates the average by adding all compound scores and dividing by the number of chunks
    
    return { # returns a dictionary with all the analysis results
        'chunkScores': chunkScores, # list of all the score dictionaries
        'chunks': chunks, # list of all the text chunks
        'averageCompound': averageCompound # the average compound score for the whole song
    }





def getSentimentLabel(compoundScore): # defines function that takes a compound score (-1.0 to 1.0) and returns a text label
    '''
    get a text label for the sentiment based on compound score.
    
    args:
        compoundScore (float): The compound sentiment score from VADER (-1.0 to 1.0)
    
    returns:
        str: A text label ("Positive", "Negative", or "Neutral")
    '''
    if compoundScore >= 0.05: # vaders's threshold for positive sentiment
        return "Positive" # returns the string "Positive"
    elif compoundScore <= -0.05: # vaders's threshold for negative sentiment
        return "Negative" # returns the string "Negative"
    else: # if the score is between -0.05 and 0.05
        return "Neutral" # returns the string "Neutral"





def formatSentimentResults(sentimentResults): # defines function that takes the results dictionary from analyzeLyrics
    '''
    format sentiment analysis results into a readable string for discord.
    
    args:
        sentimentResults (dict): Results from analyzeLyrics()
    
    returns:
        str: Formatted string with sentiment analysis
    '''
    if not sentimentResults: # checks if sentimentResults is None or empty
        return "No sentiment data available" # returns error message
    
    label = getSentimentLabel(sentimentResults['averageCompound']) # calls getSentimentLabel to convert the average compound score into a text label (Positive/Negative/Neutral)
    
    message = f"**Sentiment Analysis**\n\n" # starts building the message string, ** is Discord formatting for bold, \n\n creates two new lines
    message += f"Overall: **{label}** (Score: {sentimentResults['averageCompound']:.3f})\n\n" # adds the sentiment label and score to the message, :.3f formats the float to 3 decimal places
    
    return message # returns the formatted string





def sentimentViz(sentimentResults, artistName, songTitle, filename="sentiment_plot.png"): # defines function that creates a visualization, filename has a default value
   
    '''
    create a simple line graph showing how sentiment changes throughout the song.
    Saves the visualization as a PNG file.
    Note: i have realized that if there is just music for a while and there 
    are no lyrics, the line goes downward and appears to be negative sentiment. 
    
    args:
        sentimentResults (dict): Results from analyzeLyrics() containing chunk data
        artistName (str): Name of the artist
        songTitle (str): Title of the song
        filename (str): Name of the file to save (default: "sentiment_plot.png")
    
    returns:
        str: The filename of the saved plot

*** 
This function's code uses Claude AI suggestions. Full conversation is here: 
https://claude.ai/share/a405c4a9-7e39-4a23-b658-1238925b0039 
The following lines of code are adapted from the recommendations of this chat:
1) compoundScores = [score['compound'] for score in sentimentResults['chunkScores']]
2) chunkNumbers = list(range(1, len(compoundScores) + 1))
3) plt.plot(chunkNumbers, compoundScores)

These concepts (list comprehensions, range, matplotlib plotting) were already familiar to me. 
What I needed help with was understanding how to map each 10-word chunk to an x-axis value 
to visualize sentiment progression throughout the song.

What I learned:
- Using len(compoundScores) returns the total number of chunks
- range(1, len(compoundScores) + 1) creates a sequence [1, 2, 3, ...] up to the number of chunks
- list() converts that sequence into an actual list for plotting
- The list comprehension extracts just the 'compound' score from each chunk's sentiment data
- This gives us our x (chunkNumbers) and y (compoundScores) values for matplotlib

Equivalent longer version of the list comprehension:
    compoundScores = []
    for score in sentimentResults['chunkScores']:
        compoundScores.append(score['compound'])

And for creating the chunk numbers:
chunkNumbers = []
total_chunks = len(compoundScores)
for i in range(1, total_chunks + 1):
    chunkNumbers.append(i)
***

    '''
    
    if not sentimentResults: # checks if sentimentResults is None or empty
        return None # returns None to indicate failure
    
    # Extract compound scores from each chunk
    # following 3 lines adapted from claude code. the full prompt and result is linked above in the docstrings.
    compoundScores = [score['compound'] for score in sentimentResults['chunkScores']] # list comprehension that extracts just the compound score from each chunk
    
    # create x-axis values (chunk numbers: 1, 2, 3, 4...)
    chunkNumbers = list(range(1, len(compoundScores) + 1)) # creates a list [1, 2, 3, 4, ...] for the x-axis, +1 because range stops before the end number
    
    # create the plot
    plt.plot(chunkNumbers, compoundScores) # creates a line graph with chunk numbers on x-axis and sentiment scores on y-axis
    
    # add labels and title
    plt.xlabel('Song Progression') # sets the x-axis label which is for each chunk of 10 words 
    plt.ylabel('Sentiment Score') # sets the y-axis label
    plt.title(f'{songTitle} by {artistName}') # sets the title of the plot using an f-string
    
    # save the plot
    plt.savefig(filename) # saves the plot as a PNG file with the given filename
    plt.clf() # "clear figure" - clears the plot so the next plot doesn't overlap with this one
    
    return filename # returns the filename so the bot knows where to find the saved image