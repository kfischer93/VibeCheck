import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

nltk.download("vader_lexicon", quiet=True)

vaderSIA = SentimentIntensityAnalyzer()


def analyzeLyrics(lyrics, chunkSize=10):
    if not lyrics:
        return None
    
    words = lyrics.split()
    
    if len(words) <= chunkSize:
        overallScores = vaderSIA.polarity_scores(lyrics)
        return {
            'chunkScores': [overallScores],
            'chunks': [lyrics],
            'averageCompound': overallScores['compound']
        }
    
    chunkScores = []
    chunks = []
    
    for i in range(0, len(words), chunkSize):
        chunk = " ".join(words[i:i + chunkSize])
        scores = vaderSIA.polarity_scores(chunk)
        chunks.append(chunk)
        chunkScores.append(scores)
    
    compoundScores = [score['compound'] for score in chunkScores]
    averageCompound = sum(compoundScores) / len(compoundScores)
    
    return {
        'chunkScores': chunkScores,
        'chunks': chunks,
        'averageCompound': averageCompound
    }


def getSentimentLabel(compoundScore):
    if compoundScore >= 0.05:
        return "Positive"
    elif compoundScore <= -0.05:
        return "Negative"
    else:
        return "Neutral"


def formatSentimentResults(sentimentResults):
    if not sentimentResults:
        return "No sentiment data available"
    
    label = getSentimentLabel(sentimentResults['averageCompound'])
    
    message = f"**Sentiment Analysis**\n\n"
    message += f"Overall: **{label}** (Score: {sentimentResults['averageCompound']:.3f})\n\n"
    
    return message


def sentimentViz(sentimentResults, artistName, songTitle, filename="sentiment_plot.png"):
    if not sentimentResults:
        return None
    
    compoundScores = [score['compound'] for score in sentimentResults['chunkScores']]
    chunkNumbers = list(range(1, len(compoundScores) + 1))
    
    plt.plot(chunkNumbers, compoundScores)
    plt.xlabel('Song Progression')
    plt.ylabel('Sentiment Score')
    plt.title(f'{songTitle} by {artistName}')
    plt.savefig(filename)
    plt.clf()
    
    return filename
