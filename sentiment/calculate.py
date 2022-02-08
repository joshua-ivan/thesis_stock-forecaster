from multiprocessing import Pool, Queue, cpu_count
from utilities import file_io, date_util, input_validation
import config
import pandas
import re
import warnings
import os


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


def process_posts(arguments):
    directory = arguments['full_paths']
    aggregate_data = arguments['aggregate_data']
    sentiment_calculator = SentimentCalculator()
    word_counts_dir = 'counts'

    sentiment_data = pandas.DataFrame(columns=['Filename', 'Date', 'Length', 'Negative', 'Positive', 'Sentiment'])
    date_dirs = os.listdir(directory)
    for date_dir in date_dirs:
        files = os.listdir(f'{directory}/{date_dir}')
        for file in files:
            post = file_io.read_file(f'{directory}/{date_dir}/{file}')
            counts = sentiment_calculator.count_words(post, file)
            sentiment_data = sentiment_data.append({
                'Filename': file,
                'Date': date_dir,
                'Length': counts['length'],
                'Negative': counts['negative'],
                'Positive': counts['positive'],
                'Sentiment': counts['sentiment']
            }, ignore_index=True)

    query = directory.split('/')[1]
    if not os.path.exists(word_counts_dir):
        os.makedirs(word_counts_dir)
    sentiment_data.to_csv(f'{word_counts_dir}/{query}.csv', index=False)

    aggregate_data.put(
        aggregate_sentiment_bins(
            query_to_ticker(query), sentiment_data, config.end_date, config.raw_data_interval_days, config.bin_size))


def query_to_ticker(string):
    tokens = string.split('"')
    warning_message = f'Query {string} is malformed'
    if len(tokens) < 2 or tokens[1] == "" or tokens[1].isspace():
        warnings.warn(warning_message)
        return tokens[0]
    else:
        return tokens[1]


def aggregate_sentiment_bins(ticker, dataframe, end_date, timeframe_days, interval):
    input_validation.check_nonempty_string(ticker, f'aggregate_sentiment_bins: {ticker} is not a nonempty string')
    bins = date_util.generate_bin_boundaries(end_date, timeframe_days, interval)
    aggregates = [ticker]
    for _bin in bins:
        df_bin = dataframe[dataframe['Date'].between(_bin['start'], _bin['end'])]
        bin_mean = df_bin['Sentiment'].mean() if len(df_bin) > 0 else 0
        aggregates.append(bin_mean)
    return aggregates


def construct_post_paths(base_dir):
    paths = []
    queries = os.listdir(base_dir)
    for query in queries:
        paths.append(f'{base_dir}/{query}')
    return paths


def execute():
    full_paths = construct_post_paths('clean_posts')
    aggregate_data = Queue()
    thread_pool = Pool(processes=cpu_count())
    thread_pool.map(process_posts, {
        'full_paths': full_paths,
        'aggregate_data': aggregate_data
    })
    thread_pool.terminate()

    aggregates = pandas.DataFrame(columns=date_util.generate_aggregate_columns(
        config.end_date, config.raw_data_interval_days, config.bin_size))
    while not aggregate_data.empty():
        row = aggregate_data.get()
        aggregates.iloc[len(aggregates)] = row
    aggregates.to_csv('sentiment.csv', index=False)
