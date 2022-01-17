from multiprocessing import Pool, cpu_count
from utilities import file_io
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


def process_posts(directory):
    subdirectories = directory.split('/')
    query = subdirectories[1]
    date = subdirectories[2]
    sentiment_calculator = SentimentCalculator()

    sentiment_data = pandas.DataFrame(columns=['Filename', 'Length', 'Negative', 'Positive'])
    files = os.listdir(directory)
    for file in files:
        post = file_io.read_file(f'{directory}/{file}')
        counts = sentiment_calculator.count_words(post, file)
        sentiment_data = sentiment_data.append({
            'Filename': file,
            'Date': date,
            'Length': counts['length'],
            'Negative': counts['negative'],
            'Positive': counts['positive'],
            'Sentiment': counts['sentiment']
        }, ignore_index=True)

    output_dir = 'counts'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    sentiment_data.to_csv(f'counts/{query}.csv', index=False)


def execute():
    base_dir = 'clean_posts'
    full_paths = []
    post_directories = os.listdir(base_dir)
    for post_dir in post_directories:
        date_dirs = os.listdir(f'{base_dir}/{post_dir}')
        for date_dir in date_dirs:
            full_paths.append(f'{base_dir}/{post_dir}/{date_dir}')

    thread_pool = Pool(processes=cpu_count())
    thread_pool.map(process_posts, full_paths)
    thread_pool.terminate()
