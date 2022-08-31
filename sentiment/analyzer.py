from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.preprocessing import MultiLabelBinarizer
from sentiment.post_sentiment import PostSentiment
from sentiment.tokenizer import TickerTokenizer
from sentiment.scaler import ScoreScaler
from utilities import file_io
from itertools import chain
from collections import Counter
import pandas
import numpy
import datetime
import re
import os


class RedditAnalyzer:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()
        self.stock_tickers = pandas.read_csv('intermediate_data/tickers.csv')
        self.tokenizer = TickerTokenizer(self.stock_tickers['Symbol'])
        self.os = os

    def parse_tickers(self, text):
        words = self.tokenizer.word_tokenize(text)
        pattern = re.compile('^\\$[A-Z]+(\\^[A-Z])?$')
        tickers = [word for word in words if pattern.match(word)]
        return [ticker for ticker in tickers
                if self.stock_tickers.loc[self.stock_tickers['Symbol'] == ticker].size > 0]

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

    def train_score_scaler(self, posts_dir, posts_df):
        scores = self.extract_post_scores(posts_dir, posts_df['filename'])
        scaler = ScoreScaler()
        scaler.fit_transform(scores)
        return scaler

    def process_post(self, post_dir, filename, scaler):
        file = file_io.read_file(f'{post_dir}/{filename}').split('\n\n\n')

        post_type = file[0]
        if post_type == 'SUBMISSION':
            title = file[1]
            tickers = self.parse_tickers(title)
        elif post_type == 'COMMENT':
            submission_filename = file[1]
            submission_sentiment = self.process_post(post_dir, submission_filename, scaler)
            tickers = submission_sentiment.tickers
        else:
            # malformed file contents; skip
            return

        content = file[3]
        tickers = list(set(tickers) | set(self.parse_tickers(content)))
        raw_sentiment = self.raw_score(content)

        vote_score = int(file[2])
        weighted_sentiment = raw_sentiment * scaler.transform(vote_score)
        return PostSentiment(filename, tickers, weighted_sentiment)

    def build_sentiment_dataframe(self, post_sentiments):
        post_sentiments_df = pandas.DataFrame([vars(ps) for ps in post_sentiments])
        mlb = MultiLabelBinarizer()
        matrix = pandas.DataFrame(mlb.fit_transform(post_sentiments_df['tickers']), columns=mlb.classes_)
        post_sentiments_df.drop(['tickers'], axis=1, inplace=True)
        return pandas.concat([post_sentiments_df, matrix], axis=1)

    def extract_sentiment(self, start_time, end_time):
        all_posts_dir = 'intermediate_data/posts'
        all_posts_df = self.build_posts_dataframe(all_posts_dir)

        scaler_train_df = self.filter_dataframe(all_posts_df, (end_time - (24 * 60 * 60)), end_time)
        scaler = self.train_score_scaler(all_posts_dir, scaler_train_df)

        time_filter_df = self.filter_dataframe(all_posts_df, start_time, end_time)
        post_sentiments = [(lambda post: self.process_post(all_posts_dir, post, scaler))(post)
                           for post in time_filter_df['filename']]

        binarized_df = self.build_sentiment_dataframe(post_sentiments)
        print(binarized_df.loc[binarized_df['$BBBY'] == 1])
        print(binarized_df.loc[binarized_df['$BBBY'] == 1]['sentiment'].mean())
