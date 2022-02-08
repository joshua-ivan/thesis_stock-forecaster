from multiprocessing import Pool, Manager, cpu_count
from functools import partial
from utilities import file_io, date_util, input_validation
import config
import pandas
import re
import warnings
import os


class SentimentCalculator:
    def __init__(self):
        self.dictionary = pandas.read_csv('LoughranMcDonald_MasterDictionary_2020__condensed.csv')
        self.dataframe = pandas.DataFrame(columns=['Filename', 'Date', 'Length', 'Negative', 'Positive', 'Sentiment'])

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

    def append_dataframe(self, filename, date, counts):
        self.dataframe.append({
            'Filename': filename,
            'Date': date,
            'Length': counts['length'],
            'Negative': counts['negative'],
            'Positive': counts['positive'],
            'Sentiment': counts['sentiment']
        }, ignore_index=True)

    def export_dataframe(self, filename):
        if not os.path.exists(config.counts_dir):
            os.makedirs(config.counts_dir)
        self.dataframe.to_csv(f'{config.counts_dir}/{filename}.csv', index=False)

    def aggregate_by_bin(self, ticker, end_date, data_size, bin_size):
        input_validation.check_nonempty_string(ticker, f'aggregate_by_bin: {ticker} is not a nonempty string')
        bins = date_util.generate_bin_boundaries(end_date, data_size, bin_size)
        aggregates = [ticker]
        for _bin in bins:
            df_bin = self.dataframe[self.dataframe['Date'].between(_bin['start'], _bin['end'])]
            bin_mean = df_bin['Sentiment'].mean() if len(df_bin) > 0 else 0
            aggregates.append(bin_mean)
        return aggregates


def construct_post_paths(base_dir):
    paths = []
    queries = os.listdir(base_dir)
    for query in queries:
        paths.append(f'{base_dir}/{query}')
    return paths


def process_posts(aggregate_data, directory):
    sentiment_calculator = SentimentCalculator()

    date_dirs = os.listdir(directory)
    for date_dir in date_dirs:
        files = os.listdir(f'{directory}/{date_dir}')
        for file in files:
            post = file_io.read_file(f'{directory}/{date_dir}/{file}')
            counts = sentiment_calculator.count_words(post, file)
            sentiment_calculator.append_dataframe(file, date_dir, counts)

    query = directory.split('/')[1]
    sentiment_calculator.export_dataframe(query)

    aggregate_data.put(
        sentiment_calculator.aggregate_by_bin(
            query_to_ticker(query), config.end_date, config.raw_data_interval_days, config.bin_size))


def query_to_ticker(string):
    tokens = string.split('"')
    warning_message = f'Query {string} is malformed'
    if len(tokens) < 2 or tokens[1] == "" or tokens[1].isspace():
        warnings.warn(warning_message)
        return tokens[0]
    else:
        return tokens[1]


def generate_aggregate_dataframe(columns, data_queue):
    if str(type(data_queue)) != '<class \'multiprocessing.managers.AutoProxy[Queue]\'>':
        raise TypeError('generate_aggregate_dataframe: given data is not a multiprocessing.Manager.Queue')

    dataframe = pandas.DataFrame(columns=columns)
    while not data_queue.empty():
        row = data_queue.get()
        dataframe.loc[len(dataframe)] = row
    return dataframe


def execute():
    full_paths = construct_post_paths('clean_posts')
    aggregate_data = Manager().Queue()
    thread_pool = Pool(processes=cpu_count())
    thread_pool.map(partial(process_posts, aggregate_data), full_paths)
    thread_pool.terminate()

    columns = date_util.generate_aggregate_columns(
        config.end_date, config.raw_data_interval_days, config.bin_size)
    generate_aggregate_dataframe(columns, aggregate_data).to_csv('sentiment.csv', index=False)
