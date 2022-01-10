from datetime import timedelta
from sentiment.reddit.scraper import RedditScraper
from config import stocks
import time


def build_query(keywords):
    query = f'"{keywords[0]}"'
    index = 1
    while index < len(keywords):
        query = query + f' OR "{keywords[index]}"'
        index = index + 1
    return query


def execute():
    reddit_scraper = RedditScraper()

    for stock in stocks:
        terms = [stock['ticker'], stock['company']]
        query = build_query(terms)

        end_date = time.time()
        start_date = end_date - timedelta(days=7).total_seconds()

        reddit_scraper.scrape(query, start_date, end_date, '')
