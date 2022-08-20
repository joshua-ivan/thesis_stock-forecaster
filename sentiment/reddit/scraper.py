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

    def scrape_recent_subreddit_content(self, after):
        last_fullname = after
        submissions = self.api.recent_subreddit_submissions(last_fullname)
        for submission in submissions:
            submission_filename = f'{submission.created_utc} - {submission.fullname}'
            submission_contents =\
                f'SUBMISSION\n\n\n{submission.title}\n\n\n{submission.score}\n\n\n{submission.selftext}'
            file_io.write_file(f'intermediate_data/posts/', submission_filename, submission_contents)

            comment_forest = submission.comments
            more_comments = True
            while more_comments:
                while True:
                    try:
                        more_comments = (len(comment_forest.replace_more()) > 0)
                        break
                    except Exception:
                        continue
            comment_list = comment_forest.list()
            for comment in comment_list:
                comment_filename = f'{comment.created_utc} - {comment.id}'
                comment_contents =\
                    f'COMMENT\n\n\n{submission_filename}\n\n\n{comment.score}\n\n\n{comment.body}'
                file_io.write_file(f'intermediate_data/posts/', comment_filename, comment_contents)

            last_fullname = submission.fullname
        if last_fullname != after:
            self.scrape_recent_subreddit_content(last_fullname)

    def scrape(self, sub, query, start_date, end_date, result_op, after):
        last_fullname = after
        submissions = self.api.search_subreddit(sub, query, last_fullname)
        for submission in submissions:
            last_timestamp = submission.created_utc
            if last_timestamp <= start_date:
                return
            else:
                last_fullname = submission.fullname
                if last_timestamp < end_date:
                    result_op(query, submission)
        if last_fullname != after:
            self.scrape(sub, query, start_date, end_date, result_op, last_fullname)

    def write_post(self, op_string, submission):
        date = datetime.fromtimestamp(int(submission.created_utc), tz=self.timezone).date()
        file_io.write_file(f'posts/{op_string}/{date}',
                           f'{submission.fullname}',
                           f'{submission.title}\n\n\n{submission.selftext}')
