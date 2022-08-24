from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize as nltk_tokenizer
import re


class RedditAnalyzer:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()
        self.tokenizer = nltk_tokenizer

    def parse_tickers(self, text):
        words = self.tokenizer.word_tokenize(text)
        pattern = re.compile('^\\$?[A-Z]+(\\^[A-Z])?$')
        tickers = [word for word in words if pattern.match(word)]
        for i in range(0, len(tickers)):
            tickers[i] = tickers[i].replace('$', '')
            tickers[i] = tickers[i].split('^')[0]
        return tickers

    def raw_score(self, text):
        sentences = self.tokenizer.sent_tokenize(text)
        overall_sentiment = 0.0
        for sentence in sentences:
            scores = self.sid.polarity_scores(sentence)
            overall_sentiment += scores['compound']
        return overall_sentiment

    def train_score_normalizer(self):
        # get list of all scraped posts
        # filter down to posts within a given datetime range
        # extract score list for each post
        # setup (-2, 2) normalizer with score list as input
        pass
