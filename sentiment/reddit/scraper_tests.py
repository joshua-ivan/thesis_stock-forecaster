from unittest.mock import Mock, patch, call
from sentiment.reddit.api import RedditAPI
from sentiment.reddit.scraper import RedditScraper
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from utilities import file_io
import unittest
import time


def assert_write_calls(mock_write, dates):
    calls = []
    for index in range(len(dates)):
        calls.append(call(f'posts/test_query/{dates[index]}', f't3_test{index}', f'test title\n\n\ntest contents'))
    mock_write.assert_has_calls(calls)
    pass


class RedditScraperTests(unittest.TestCase):
    def get_item_mock(self, timestamps):
        mock = []
        index = 0
        for timestamp in timestamps:
            mock.append(self.MockSubmission(timestamp, f't3_test{index}', 'test title', 'test contents'))
            index += 1
        return mock

    def generate_timestamps(self, deltas):
        timestamps = []
        for delta in deltas:
            timestamps.append(self.current_time - timedelta(days=delta).total_seconds())
        return timestamps

    def generate_dates(self, deltas):
        dates = []
        for delta in deltas:
            dates.append(datetime.fromtimestamp(int(self.current_time - timedelta(days=delta).total_seconds())).date())
        return dates

    def assert_scrape_calls(self, scrape_spy, write_op, after_fullnames):
        calls = map(
            lambda x: call('test_sub', 'test_query', self.last_week_time, self.current_time, write_op, x),
            after_fullnames)
        scrape_spy.assert_has_calls(calls)

    class MockSubmission:
        def __init__(self, created_utc, fullname, title, selftext):
            self.created_utc = created_utc
            self.fullname = fullname
            self.title = title
            self.selftext = selftext

    def setUp(self):
        self.current_time = time.time()
        self.current_date = datetime.fromtimestamp(int(self.current_time)).date()
        self.last_week_time = self.current_time - timedelta(days=7).total_seconds()

    @patch.object(RedditAPI, 'search_subreddit')
    @patch('utilities.file_io.write_file')
    def test_scrape_empty_submissions(self, mock_write, mock_search):
        mock_search.return_value = iter(())
        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test_sub', 'test_query', self.last_week_time, self.current_time, scraper.write_post, '')
            self.assert_scrape_calls(scrape_spy, scraper.write_post, '')
        mock_write.assert_not_called()

    @patch.object(RedditAPI, 'search_subreddit')
    @patch('utilities.file_io.write_file')
    def test_scrape_one_submission(self, mock_write, mock_search):
        deltas = [1]
        timestamps = self.generate_timestamps(deltas)
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test_sub', 'test_query', self.last_week_time, self.current_time, scraper.write_post, '')
            self.assert_scrape_calls(scrape_spy, scraper.write_post, ['', 't3_test0'])

        dates = self.generate_dates(deltas)
        assert_write_calls(mock_write, dates)

    @patch.object(RedditAPI, 'search_subreddit')
    @patch('utilities.file_io.write_file')
    def test_scrape_many_submissions(self, mock_write, mock_search):
        deltas = [1, 2, 3]
        timestamps = self.generate_timestamps(deltas)
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test_sub', 'test_query', self.last_week_time, self.current_time, scraper.write_post, '')
            self.assert_scrape_calls(scrape_spy, scraper.write_post, ['', 't3_test2'])

        dates = self.generate_dates(deltas)
        assert_write_calls(mock_write, dates)

    @patch.object(RedditAPI, 'search_subreddit')
    @patch('utilities.file_io.write_file')
    def test_scrape_skip_submissions_past_end_date(self, mock_write, mock_search):
        deltas = [-1, 0, 1]
        timestamps = self.generate_timestamps(deltas)
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test_sub', 'test_query', self.last_week_time, self.current_time, scraper.write_post, '')
            self.assert_scrape_calls(scrape_spy, scraper.write_post, ['', 't3_test2'])

        dates = self.generate_dates(deltas)
        mock_write.assert_has_calls([
            call(f'posts/test_query/{dates[2]}', 't3_test2', f'test title\n\n\ntest contents')
        ])

    @patch.object(RedditAPI, 'search_subreddit')
    @patch('utilities.file_io.write_file')
    def test_scrape_stop_before_start_date(self, mock_write, mock_search):
        deltas = [1, 8]
        timestamps = self.generate_timestamps(deltas)
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test_sub', 'test_query', self.last_week_time, self.current_time, scraper.write_post, '')
            self.assert_scrape_calls(scrape_spy, scraper.write_post, '')

        dates = self.generate_dates(deltas)
        mock_write.assert_has_calls([
            call(f'posts/test_query/{dates[0]}', 't3_test0', f'test title\n\n\ntest contents')
        ])

    @patch.object(RedditAPI, 'search_subreddit')
    @patch('utilities.file_io.write_file')
    def test_injectable_timezone(self, mock_write, mock_search):
        self.current_time = datetime(year=2022, month=1, day=16,
                                     hour=0, minute=0, second=0, microsecond=0,
                                     tzinfo=ZoneInfo('US/Eastern'), fold=0).timestamp()
        self.current_date = datetime.fromtimestamp(int(self.current_time)).date()
        self.last_week_time = self.current_time - timedelta(days=7).total_seconds()

        deltas = [1]
        timestamps = self.generate_timestamps(deltas)
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper('US/Pacific')
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test_sub', 'test_query', self.last_week_time, self.current_time, scraper.write_post, '')
            self.assert_scrape_calls(scrape_spy, scraper.write_post, '')

        dates = self.generate_dates(deltas)
        self.assertEqual(str(dates[0]), '2022-01-14')
        mock_write.assert_has_calls([
            call(f'posts/test_query/{dates[0]}', 't3_test0', f'test title\n\n\ntest contents')
        ])

    def test_scrape_recent_subreddit_content(self):
        scraper = RedditScraper('US/Pacific')
        scraper.api = Mock()
        scraper.scrape_comments = Mock()
        mock_io = Mock()

        scraper.api.recent_subreddit_submissions.return_value = []
        scraper.scrape_recent_subreddit_content('', mock_io)
        mock_io.assert_not_called()

        scraper.api.reset_mock()
        scraper.api.recent_subreddit_submissions.side_effect = [[Mock()], [Mock()], []]
        scraper.scrape_recent_subreddit_content('', mock_io)
        self.assertEqual(mock_io.write_file.call_count, 2)

    def test_scrape_comments_no_comments(self):
        scraper = RedditScraper('US/Pacific')
        mock_submission = Mock()
        mock_submission.comments.replace_more.return_value = []
        mock_submission.comments.list.return_value = []
        mock_io = Mock()

        scraper.scrape_comments(mock_submission, mock_io)

        mock_submission.comments.replace_more.assert_called_once()
        mock_io.assert_not_called()

    def test_scrape_comments_many_comments(self):
        scraper = RedditScraper('US/Pacific')

        mock_comment_one = Mock()
        mock_comment_one.created_utc = 555
        mock_comment_one.id = 'bar'
        mock_comment_one.score = 100
        mock_comment_one.body = 'MOCK'

        mock_comment_two = Mock()
        mock_comment_two.created_utc = 556
        mock_comment_two.id = 'baz'
        mock_comment_two.score = 101
        mock_comment_two.body = 'MOCK'

        mock_submission = Mock()
        mock_submission.created_utc = 500
        mock_submission.fullname = 'foo'
        mock_submission.comments.replace_more.return_value = []
        mock_submission.comments.list.return_value = [mock_comment_one, mock_comment_two]

        mock_io = Mock()

        scraper.scrape_comments(mock_submission, mock_io)
        mock_submission.comments.replace_more.assert_called_once()
        mock_io.write_file.assert_has_calls([
            call('intermediate_data/posts/', '555 - bar', 'COMMENT\n\n\n500 - foo\n\n\n100\n\n\nMOCK'),
            call('intermediate_data/posts/', '556 - baz', 'COMMENT\n\n\n500 - foo\n\n\n101\n\n\nMOCK')
        ])

    def test_eager_load_comments(self):
        scraper = RedditScraper('US/Pacific')
        mock_submission = Mock()

        mock_submission.comments.replace_more.return_value = []
        scraper.eager_load_comments(mock_submission)
        mock_submission.comments.replace_more.assert_called_once()

        mock_submission.reset_mock()
        mock_submission.comments.replace_more.side_effect = [['foo'], ['bar'], []]
        scraper.eager_load_comments(mock_submission)
        self.assertEqual(mock_submission.comments.replace_more.call_count, 3)

    def test_run_recent_scraper(self):
        scraper = RedditScraper('US/Pacific')
        # scraper.scrape_recent_subreddit_content('', file_io)

    if __name__ == '__main__':
        unittest.main()
