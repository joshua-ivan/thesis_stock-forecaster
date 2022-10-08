from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.preprocessing import MultiLabelBinarizer
from sentiment.post_sentiment import PostSentiment
from sentiment.tokenizer import TickerTokenizer
from sentiment.scaler import ScoreScaler
from sentiment.lexicon import wsb_lexicon
from utilities import file_io
from itertools import chain
from collections import Counter
import pandas
import numpy
import re
import os


class RedditAnalyzer:
    def __init__(self, lex=wsb_lexicon):
        self.sid = SentimentIntensityAnalyzer()
        self.update_lexicon(lex)
        self.stock_tickers = pandas.read_csv('../forecaster_data/tickers.csv')
        self.tokenizer = TickerTokenizer(self.stock_tickers['Symbol'])
        self.scaler = ScoreScaler()
        self.os = os

        self.all_posts_dir = '../forecaster_data/posts'
        self.all_posts_df = self.build_posts_dataframe()

        self.sentiment_memo = pandas.DataFrame(columns=['timestamp', 'filename', 'sentiment'])
        self.sentiment_memo.set_index('timestamp')
        self.sentiment_memo['timestamp'] = self.sentiment_memo['timestamp'].astype('int64')

        self.file_io = file_io
        self.file_memo = {}

    def parse_tickers(self, text):
        words = self.tokenizer.word_tokenize(text)
        pattern = re.compile('^\\$[A-Z]+(\\^[A-Z])?$')
        tickers = [word for word in words if pattern.match(word)]
        return [ticker for ticker in tickers if self.stock_tickers.loc[self.stock_tickers['Symbol'] == ticker].size > 0]

    def update_lexicon(self, lex):
        self.sid.lexicon.update(lex)

    def raw_score(self, text):
        sentences = self.tokenizer.sent_tokenize(text)
        overall_sentiment = 0.0
        for sentence in sentences:
            scores = self.sid.polarity_scores(sentence)
            overall_sentiment += scores['compound']
        return overall_sentiment

    def build_time_file_tuples(self, filenames):
        return [(lambda s: (s.split(' - ')[0].split('.')[0], s))(s) for s in filenames]

    def build_posts_dataframe(self):
        all_posts = self.os.listdir(self.all_posts_dir)
        tuples = self.build_time_file_tuples(all_posts)
        posts_df = pandas.DataFrame(tuples, columns=['timestamp', 'filename'])
        posts_df.set_index('timestamp')
        posts_df['timestamp'] = posts_df['timestamp'].astype('int64')
        return posts_df

    def filter_dataframe(self, dataframe, start_time, end_time):
        return dataframe[dataframe['timestamp'].between(start_time, end_time)]

    def cached_read_file(self, filename):
        cache = self.file_memo.get(filename)
        if cache is not None:
            return cache
        else:
            text = self.file_io.read_file(f'{self.all_posts_dir}/{filename}')
            self.file_memo[filename] = text
            return text

    def extract_post_scores(self, filenames):
        scores = [(lambda p: int(self.cached_read_file(p).split('\n\n\n')[2]))(p) for p in filenames]
        return numpy.array(scores)

    def train_score_scaler(self, posts_df):
        scores = self.extract_post_scores(posts_df['filename'])
        self.scaler.fit_transform(scores)

    def process_post(self, filename):
        file = self.cached_read_file(filename).split('\n\n\n')

        post_type = file[0]
        if post_type == 'SUBMISSION':
            title = file[1]
            tickers = self.parse_tickers(title)
        elif post_type == 'COMMENT':
            submission_filename = file[1]
            submission_sentiment = self.cached_process_post(submission_filename)
            tickers = submission_sentiment.tickers
        else:
            # malformed file contents; skip
            return

        content = file[3]
        tickers = list(set(tickers) | set(self.parse_tickers(content)))
        if len(tickers) <= 0:
            return PostSentiment(filename, tickers, 0.0)
        else:
            raw_sentiment = self.raw_score(content)
            vote_score = int(file[2])
            weighted_sentiment = raw_sentiment * self.scaler.transform(vote_score)
            return PostSentiment(filename, tickers, weighted_sentiment)

    def cached_process_post(self, filename):
        memo = self.sentiment_memo.loc[self.sentiment_memo['filename'] == filename]
        if len(memo) > 0:
            return memo['sentiment'].values[0]
        else:
            ps = self.process_post(filename)
            timestamp = int(ps.filename.split(' - ')[0].split('.')[0])
            self.sentiment_memo.loc[timestamp] = [timestamp, ps.filename, ps]
            return ps

    def build_sentiment_dataframe(self, post_sentiments):
        post_sentiments_df = pandas.DataFrame([vars(ps) for ps in post_sentiments])
        mlb = MultiLabelBinarizer()
        matrix = pandas.DataFrame(mlb.fit_transform(post_sentiments_df['tickers']), columns=mlb.classes_)
        post_sentiments_df.drop(['tickers'], axis=1, inplace=True)
        return pandas.concat([post_sentiments_df, matrix], axis=1)

    def extract_frequency(self, post_sentiments):
        post_sentiments_df = pandas.DataFrame([vars(ps) for ps in post_sentiments])
        freq = pandas.Series(Counter(chain.from_iterable(post_sentiments_df['tickers']))).sort_values(ascending=False)
        return freq

    def extract_sentiment(self, start_time, end_time):
        scaler_train_df = self.filter_dataframe(self.all_posts_df, (end_time - (60 * 60 * 24 * 5)), end_time)
        self.train_score_scaler(scaler_train_df)

        self.sentiment_memo = self.filter_dataframe(self.sentiment_memo, start_time, end_time)
        time_filter_df = self.filter_dataframe(self.all_posts_df, start_time, end_time)
        post_sentiments = [self.cached_process_post(post) for post in time_filter_df['filename']]

        frequency_series = self.extract_frequency(post_sentiments)
        most_frequent_ticker = frequency_series.keys()[0]
        binarized_df = self.build_sentiment_dataframe(post_sentiments)
        return most_frequent_ticker, binarized_df.loc[binarized_df[most_frequent_ticker] == 1]['sentiment'].mean()
