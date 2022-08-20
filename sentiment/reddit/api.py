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

    def recent_subreddit_submissions(self, after):
        return self.reddit.subreddit('wallstreetbets').new(params={'after': after})

    def search_subreddit(self, sub, query, after):
        return self.reddit.subreddit(sub).search(query=query, sort='new', params={'after': after})

    def search(self, query, after):
        return self.search_subreddit('all', query, after)
