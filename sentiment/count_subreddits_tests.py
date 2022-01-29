from sentiment.count_subreddits import SubredditCounter
from utilities.pandas_util import extract_cell
import unittest


class MockSubmission:
    def __init__(self, subreddit_name):
        class MockSubreddit:
            def __init__(self, name):
                self.name = name

        self.subreddit = MockSubreddit(subreddit_name)


class CountSubredditTests(unittest.TestCase):
    def test_increment(self):
        mock_submissions = {
            MockSubmission('linux'),
            MockSubmission('windows'),
            MockSubmission('linux'),
            MockSubmission('macintosh')}
        subreddit_counter = SubredditCounter()

        for mock in mock_submissions:
            subreddit_counter.increment(query='MOCK', submission=mock)

        self.assertEqual(len(subreddit_counter.count), 3)
        self.assertEqual(extract_cell(subreddit_counter.count, 'Subreddit', 'linux', 'Count'), 2)
        self.assertEqual(extract_cell(subreddit_counter.count, 'Subreddit', 'windows', 'Count'), 1)
        self.assertEqual(extract_cell(subreddit_counter.count, 'Subreddit', 'macintosh', 'Count'), 1)
