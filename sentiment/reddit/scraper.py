from sentiment.reddit.api import RedditAPI
from datetime import datetime
from zoneinfo import ZoneInfo
from utilities import file_io
import logging


def setup_reddit_logger():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    for logger_name in ("praw", "prawcore"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)


class RedditScraper:
    def __init__(self, timezone=None):
        self.timezone = ZoneInfo(timezone) if timezone is not None else None
        self.api = RedditAPI()
        setup_reddit_logger()

    def search_all(self, query, start_date, end_date, after):
        last_fullname = after
        submissions = self.api.search(query, last_fullname)
        for submission in submissions:
            last_timestamp = submission.created_utc
            if last_timestamp <= start_date:
                return
            else:
                last_fullname = submission.fullname
                if last_timestamp < end_date:
                    date = datetime.fromtimestamp(int(submission.created_utc), tz=self.timezone).date()
                    file_io.write_file(f'posts/{query}/{date}',
                                       f'{submission.fullname}',
                                       f'{submission.title}\n\n\n{submission.selftext}')
        if last_fullname != after:
            self.search_all(query, start_date, end_date, last_fullname)
