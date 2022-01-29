from datetime import timedelta
from sentiment.reddit.scraper import RedditScraper
from config import stocks
import sentiment.reddit.query as reddit_query
import time


def execute():
    reddit_scraper = RedditScraper()

    for stock in stocks:
        terms = [stock['ticker'], stock['company']]
        end_date = time.time()
        start_date = end_date - timedelta(days=730).total_seconds()

        reddit_scraper.search_all(reddit_query.build(terms), start_date, end_date, reddit_scraper.write_post, '')
