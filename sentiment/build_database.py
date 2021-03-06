from datetime import timedelta
from sentiment.reddit.scraper import RedditScraper
from config import subreddits, stocks, raw_data_interval_days
import sentiment.reddit.query as reddit_query
import time


def execute():
    reddit_scraper = RedditScraper()

    for sub in subreddits:
        for stock in stocks:
            terms = [stock['ticker'], stock['company']]
            end_date = time.time()
            start_date = end_date - timedelta(days=raw_data_interval_days).total_seconds()

            reddit_scraper.scrape(sub, reddit_query.build(terms), start_date, end_date, reddit_scraper.write_post, '')
