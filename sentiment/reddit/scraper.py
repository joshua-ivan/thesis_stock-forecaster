from sentiment.reddit.api import RedditAPI
import os


def write_submission(directory, filename, content):
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        with open(f'{directory}/{filename}', 'w', encoding='utf-8') as file:
            file.write(content)
            file.close()
    except OSError as error:
        print(error)


class RedditScraper:
    def __init__(self):
        self.api = RedditAPI()

    def scrape(self, query, start_date, end_date, after):
        last_fullname = after
        submissions = self.api.search(query, last_fullname)
        for submission in submissions:
            last_timestamp = submission.created_utc
            if last_timestamp <= start_date:
                return
            else:
                last_fullname = submission.fullname
                if last_timestamp < end_date:
                    write_submission(f'posts/{query}',
                                     f'{submission.created_utc} - {submission.fullname}',
                                     f'{submission.title}\n\n\n{submission.selftext}')
        if last_fullname != after:
            self.scrape(query, start_date, end_date, after)
