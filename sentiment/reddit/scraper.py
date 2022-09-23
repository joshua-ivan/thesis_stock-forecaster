from sentiment.reddit.api import RedditAPI
from datetime import datetime
from zoneinfo import ZoneInfo
from utilities import file_io
import logging


def setup_reddit_logger():
    handler = logging.StreamHandler()
    handler.setLevel(logging.ERROR)
    for logger_name in ("praw", "prawcore"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.ERROR)
        logger.addHandler(handler)


class RedditScraper:
    def __init__(self, timezone=None):
        self.timezone = ZoneInfo(timezone) if timezone is not None else None
        self.api = RedditAPI()
        setup_reddit_logger()

    def scrape_daterange_subreddit_content(self, start_date, end_date, io):
        current_start = start_date
        current_end = start_date + (60 * 60)

        while current_start < end_date:
            print(f'current_start: {current_start} | current_end: {current_end}')
            submission_ids = self.api.submission_ids(current_start, current_end)
            print(submission_ids)

            for _id in submission_ids:
                submission = self.api.get_submission(_id)
                try:
                    submission_filename = f'{submission.created_utc} - {submission.fullname}'
                    submission_contents = \
                        f'SUBMISSION\n\n\n{submission.title}\n\n\n{submission.score}\n\n\n{submission.selftext}'
                    # print(f'intermediate_data/posts/{submission_filename}\n{submission_contents}')
                    io.write_file(f'intermediate_data/posts/', submission_filename, submission_contents)
                except AttributeError as ae:
                    print(f'{ae}\nbad submission: {_id}')
                    continue
                self.scrape_comments(submission, io)

            current_start = current_end
            current_end = current_end + (60 * 60)

    def scrape_recent_subreddit_content(self, after, io):
        last_fullname = after
        submissions = self.api.recent_subreddit_submissions(last_fullname)

        for submission in submissions:
            try:
                submission_filename = f'{submission.created_utc} - {submission.fullname}'
                submission_contents = \
                    f'SUBMISSION\n\n\n{submission.title}\n\n\n{submission.score}\n\n\n{submission.selftext}'
                io.write_file(f'intermediate_data/posts/', submission_filename, submission_contents)
            except AttributeError as ae:
                print(f'{ae}\nbad submission: {submission.id}')
            self.scrape_comments(submission, io)
            last_fullname = submission.fullname

        if last_fullname != after:
            self.scrape_recent_subreddit_content(last_fullname, io)

    def scrape_comments(self, submission, io):
        submission_filename = f'{submission.created_utc} - {submission.fullname}'

        self.eager_load_comments(submission)

        comment_list = submission.comments.list()
        for comment in comment_list:
            comment_filename = f'{comment.created_utc} - {comment.id}'
            comment_contents = \
                f'COMMENT\n\n\n{submission_filename}\n\n\n{comment.score}\n\n\n{comment.body}'
            # print(f'intermediate_data/posts/{comment_filename}\n{comment_contents}')
            io.write_file(f'intermediate_data/posts/', comment_filename, comment_contents)

    def eager_load_comments(self, submission):
        more_comments = True
        while more_comments:
            while True:
                try:
                    more_comments = (len(submission.comments.replace_more()) > 0)
                    break
                except Exception as ex:
                    print(ex)
                    continue
        return submission

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
