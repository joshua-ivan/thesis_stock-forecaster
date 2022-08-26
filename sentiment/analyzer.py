from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize as nltk_tokenizer
from sentiment.scaler import SentimentScaler
from utilities import file_io
import pandas
import numpy
import datetime
import re
import os


class RedditAnalyzer:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()
        self.tokenizer = nltk_tokenizer
        self.os = os

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

    def build_time_file_tuples(self, filenames):
        return [(lambda s: (s.split(' - ')[0].split('.')[0], s))(s) for s in filenames]

    def build_posts_dataframe(self, posts_dir):
        all_posts = self.os.listdir(posts_dir)
        tuples = self.build_time_file_tuples(all_posts)
        posts_df = pandas.DataFrame(tuples, columns=['timestamp', 'filename'])
        posts_df.set_index('timestamp')
        posts_df['timestamp'] = posts_df['timestamp'].astype('int64')
        return posts_df

    def filter_dataframe(self, dataframe, start_time, end_time):
        return dataframe[dataframe['timestamp'].between(start_time, end_time)]

    def extract_post_scores(self, post_dir, filenames):
        scores = [(lambda p: int(file_io.read_file(f'{post_dir}/{p}').split('\n\n\n')[2]))(p) for p in filenames]
        return numpy.array(scores)

    def train_score_scaler(self):
        posts_dir = 'intermediate_data/posts'
        posts_df = self.build_posts_dataframe(posts_dir)
        posts_df = self.filter_dataframe(
            posts_df,
            int(datetime.datetime(2022, 8, 23, 0, 30, 0).timestamp()),
            int(datetime.datetime(2022, 8, 24, 0, 30, 0).timestamp())
        )

        scores = self.extract_post_scores(posts_dir, posts_df['filename'])
        scaler = SentimentScaler()
        scaler.fit_transform(scores)
        return scaler
