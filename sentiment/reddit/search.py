import praw

reddit = praw.Reddit()

class RedditSearcher

def get_submissions(after):
    for submission in reddit.subreddit("all").search(query='amzn', sort='new', limit=1, params={'after': after}):
        title = submission.title
        fullname = submission.name
        print(str(title.encode('utf8')))
        print(str(fullname.encode('utf8')))
        return fullname


def go():
    after = ''
    after = get_submissions(after)
    get_submissions(after)


go()
