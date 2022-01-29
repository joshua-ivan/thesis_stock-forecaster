from sentiment.reddit.scraper import RedditScraper
from config import stocks
from datetime import timedelta
import sentiment.reddit.query as reddit_query
import pandas
import time


class SubredditCounter:
    def __init__(self):
        self.count = pandas.DataFrame(columns=['Subreddit', 'Count'])

    def increment(self, query, submission):
        subreddit = submission.subreddit.name
        row_index = self.count['Subreddit'] == subreddit
        if len(self.count.loc[row_index]) > 0:
            self.count.loc[row_index, 'Count'] = self.count.loc[row_index, 'Count'] + 1
        else:
            self.count.loc[len(self.count)] = {'Subreddit': subreddit, 'Count': 1}

    def export(self):
        self.count.to_csv('subreddit_count.csv', index=False)


def execute():
    reddit_scraper = RedditScraper()
    subreddit_counter = SubredditCounter()

    for stock in stocks:
        terms = [stock['ticker'], stock['company']]
        end_date = time.time()
        start_date = end_date - timedelta(days=730).total_seconds()

        reddit_scraper.search_all(reddit_query.build(terms), start_date, end_date, subreddit_counter.increment, '')
