from pushshift_py import PushshiftAPI
from prawcore import Requestor
import config
import praw
import json


class JSONDebugRequestor(Requestor):
    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)
        print(json.dumps(response.json(), indent=4))
        return response


class RedditAPI:
    def __init__(self):
        self.reddit = praw.Reddit(requestor_class=JSONDebugRequestor) if config.debug_responses else praw.Reddit()
        self.pushshift = PushshiftAPI()

    def submission_ids(self, start_date, end_date):
        generator = self.pushshift.search_submissions(
            subreddit='wallstreetbets', after=start_date, before=end_date, filter=['id'])

        submission_ids = []
        for request in generator:
            submission_ids.append(request)
        return list(set([(lambda sub: sub.id)(sub) for sub in submission_ids]))

    def get_submission(self, submission_id):
        return self.reddit.submission(id=submission_id)

    def recent_subreddit_submissions(self, after):
        return self.reddit.subreddit('wallstreetbets').new(params={'after': after})

    def search_subreddit(self, sub, query, after):
        return self.reddit.subreddit(sub).search(query=query, sort='new', params={'after': after})

    def search(self, query, after):
        return self.search_subreddit('all', query, after)
