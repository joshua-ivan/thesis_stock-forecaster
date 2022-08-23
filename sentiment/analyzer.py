from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize as nltk_tokenizer


class RedditAnalyzer:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()
        self.tokenizer = nltk_tokenizer

    def raw_score(self, text):
        sentences = self.tokenizer.sent_tokenize(text)
        overall_sentiment = 0.0
        for sentence in sentences:
            scores = self.sid.polarity_scores(sentence)
            overall_sentiment += scores['compound']
        return overall_sentiment
