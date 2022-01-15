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

        return {
            'length': len(word_list),
            'negative': negative,
            'positive': positive
        }


def process_posts(directory):
    sentiment_calculator = SentimentCalculator()

    sentiment_data = pandas.DataFrame(columns=['Filename', 'Length', 'Negative', 'Positive'])
    files = os.listdir(directory)
    for file in files:
        post = file_io.read_file(f'{directory}/{file}')
        counts = sentiment_calculator.count_words(post, file)
        sentiment_data = sentiment_data.append({
            'Filename': file,
            'Length': counts['length'],
            'Negative': counts['negative'],
            'Positive': counts['positive']
        }, ignore_index=True)

    sentiment_data.to_csv(f'counts/{directory}.csv', index=False)


def execute():
    base_dir = 'clean_posts'
    post_directories = os.listdir(base_dir)
    for post_dir in post_directories:
        process_posts(f'{base_dir}/{post_dir}')
