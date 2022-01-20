from multiprocessing import Pool, cpu_count
from utilities import file_io
import pandas
import re
import warnings
import os


WORD_COUNTS_DIR = 'counts'


class SentimentCalculator:
    def __init__(self):
        self.dictionary = pandas.read_csv('LoughranMcDonald_MasterDictionary_2020__condensed.csv')

    def count_words(self, post, title):
        if not isinstance(post, str):
            raise TypeError('SentimentCalculator.count_words expects an input string')

        if not re.match('^[A-Za-z0-9 \n]+$', post):
            warnings.warn(f'Post \'{title}\' has not been properly cleaned')

        word_list = post.split()
        negative = 0
        positive = 0

        for word in word_list:
            lookup = self.dictionary[self.dictionary['Word'] == word.upper()]
            if len(lookup) == 1:
                negative = negative + int(lookup['Negative'])
                positive = positive + int(lookup['Positive'])

        post_length = len(word_list)
        return {
            'length': post_length,
            'negative': negative,
            'positive': positive,
            'sentiment': (positive - negative) / post_length
        }


def process_posts(directory):
    sentiment_calculator = SentimentCalculator()

    sentiment_data = pandas.DataFrame(columns=['Filename', 'Date', 'Length', 'Negative', 'Positive', 'Sentiment'])
    dates = os.listdir(directory)
    for date in dates:
        files = os.listdir(f'{directory}/{date}')
        for file in files:
            post = file_io.read_file(f'{directory}/{date}/{file}')
            counts = sentiment_calculator.count_words(post, file)
            sentiment_data = sentiment_data.append({
                'Filename': file,
                'Date': date,
                'Length': counts['length'],
                'Negative': counts['negative'],
                'Positive': counts['positive'],
                'Sentiment': counts['sentiment']
            }, ignore_index=True)

    query = directory.split('/')[1]
    if not os.path.exists(WORD_COUNTS_DIR):
        os.makedirs(WORD_COUNTS_DIR)
    sentiment_data.to_csv(f'{WORD_COUNTS_DIR}/{query}.csv', index=False)


def query_to_ticker(string):
    tokens = string.split('"')
    warning_message = f'Query {string} is malformed'
    if len(tokens) < 2 or tokens[1] == "" or tokens[1].isspace():
        warnings.warn(warning_message)
        return tokens[0]
    else:
        return tokens[1]


def aggregate_sentiment():
    mean_sentiments = pandas.DataFrame(columns=['Ticker', 'Sentiment'])

    files = os.listdir(WORD_COUNTS_DIR)
    for file in files:
        mean_sentiments = mean_sentiments.append({
            'Ticker': query_to_ticker(file),
            'Sentiment': pandas.read_csv(f'{WORD_COUNTS_DIR}/{file}')['Sentiment'].mean()
        }, ignore_index=True)

    mean_sentiments.to_csv('sentiment.csv', index=False)


def construct_post_paths(base_dir):
    paths = []
    queries = os.listdir(base_dir)
    for query in queries:
        paths.append(f'{base_dir}/{query}')
    return paths


def execute():
    full_paths = construct_post_paths('clean_posts')
    thread_pool = Pool(processes=cpu_count())
    thread_pool.map(process_posts, full_paths)
    thread_pool.terminate()

    aggregate_sentiment()
