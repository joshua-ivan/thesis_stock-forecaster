from nltk.sentiment.vader import SentimentIntensityAnalyzer, VaderConstants
from nltk.corpus import stopwords
from sentiment.tokenizer import TickerTokenizer
from utilities import file_io
from multiprocess.pool import Pool
import pandas
import os


class FrequencyAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stock_tickers = pandas.read_csv('intermediate_data/tickers.csv')
        self.tokenizer = TickerTokenizer(self.stock_tickers['Symbol'])
        self.stopwords = stopwords.words('english')
        self.file_io = file_io

    def process_posts(self, base_dir, posts):
        unlisted_words = {}
        for post in posts:
            text = self.file_io.read_file(f'{base_dir}/{post}')
            words = self.tokenizer.word_tokenize(text)
            for word in words:
                if not word.isalpha():
                    continue

                lower = word.lower()
                if lower in self.stopwords or lower in VaderConstants.BOOSTER_DICT or lower in VaderConstants.NEGATE:
                    continue

                if self.sia.lexicon.get(lower) is None:
                    count = unlisted_words.get(lower)
                    unlisted_words[lower] = 1 if count is None else (count + 1)
        return unlisted_words

    def merge_frequency_dicts(self, dicts):
        merged = {}
        if not isinstance(dicts, list) or len(dicts) <= 0:
            return merged

        for _dict in dicts:
            if not isinstance(_dict, dict):
                continue
            for key in _dict.keys():
                merged_count, dict_count = merged.get(key), _dict[key]
                merged[key] = dict_count if merged_count is None else (merged_count + dict_count)
        return merged

    def split_post_list(self, posts, sublist_count):
        sublist_length = int(len(posts) / sublist_count)
        sublists = []
        for i in range(0, sublist_count):
            start_index = i * sublist_length
            end_index = (i + 1) * sublist_length if i < (sublist_count - 1) else len(posts)
            sublists.append(posts[start_index:end_index])
        return sublists

    def extract_word_frequency(self):
        base_dir = 'intermediate_data/posts'
        cpu_count = os.cpu_count()
        post_lists = self.split_post_list(os.listdir(base_dir), cpu_count)

        process_pool = Pool(cpu_count)
        unlisted_words = process_pool.map_async(
            lambda process: self.process_posts(base_dir, post_lists[process]),
            range(cpu_count))
        process_pool.close()
        unlisted_words = self.merge_frequency_dicts(unlisted_words.get())

        unlisted_df = pandas.DataFrame.from_dict(unlisted_words, orient='index', columns=['count'])
        unlisted_df.sort_values(by='count', ascending=False, inplace=True)
        unlisted_df.to_csv('intermediate_data/unlisted_words.csv')
