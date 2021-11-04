import praw


class RedditAPI:
    def __init__(self):
        self.reddit = praw.Reddit()

    def search(self, query, after):
        return self.reddit.subreddit("all").search(query=query, sort='new', params={'after': after})
