from unittest.mock import patch, call
from sentiment.reddit.api import RedditAPI
from sentiment.reddit.scraper import RedditScraper
from datetime import datetime, timedelta
import unittest
import time


def assert_write_calls(mock_write, dates):
    calls = []
    for index in range(len(dates)):
        calls.append(call(f'posts/test/{dates[index]}', f't3_test{index}', f'test title\n\n\ntest contents'))
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

    def assert_scrape_calls(self, scrape_spy, after_fullnames):
        calls = map(lambda x: call('test', self.last_week_time, self.current_time, x), after_fullnames)
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

    @patch.object(RedditAPI, 'search')
    @patch('utilities.file_io.write_file')
    def test_scrape_empty_submissions(self, mock_write, mock_search):
        mock_search.return_value = iter(())
        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test', self.last_week_time, self.current_time, '')
            self.assert_scrape_calls(scrape_spy, '')
        mock_write.assert_not_called()

    @patch.object(RedditAPI, 'search')
    @patch('utilities.file_io.write_file')
    def test_scrape_one_submission(self, mock_write, mock_search):
        deltas = [1]
        timestamps = self.generate_timestamps(deltas)
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test', self.last_week_time, self.current_time, '')
            self.assert_scrape_calls(scrape_spy, ['', 't3_test0'])

        dates = self.generate_dates(deltas)
        assert_write_calls(mock_write, dates)

    @patch.object(RedditAPI, 'search')
    @patch('utilities.file_io.write_file')
    def test_scrape_many_submissions(self, mock_write, mock_search):
        deltas = [1, 2, 3]
        timestamps = self.generate_timestamps(deltas)
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test', self.last_week_time, self.current_time, '')
            self.assert_scrape_calls(scrape_spy, ['', 't3_test2'])

        dates = self.generate_dates(deltas)
        assert_write_calls(mock_write, dates)

    @patch.object(RedditAPI, 'search')
    @patch('utilities.file_io.write_file')
    def test_scrape_skip_submissions_past_end_date(self, mock_write, mock_search):
        deltas = [-1, 0, 1]
        timestamps = self.generate_timestamps(deltas)
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test', self.last_week_time, self.current_time, '')
            self.assert_scrape_calls(scrape_spy, ['', 't3_test2'])

        dates = self.generate_dates(deltas)
        mock_write.assert_has_calls([
            call(f'posts/test/{dates[2]}', 't3_test2', f'test title\n\n\ntest contents')
        ])

    @patch.object(RedditAPI, 'search')
    @patch('utilities.file_io.write_file')
    def test_scrape_stop_before_start_date(self, mock_write, mock_search):
        deltas = [1, 8]
        timestamps = self.generate_timestamps(deltas)
        mock_search.return_value = iter(self.get_item_mock(timestamps))

        scraper = RedditScraper()
        with patch.object(scraper, 'scrape', wraps=scraper.scrape) as scrape_spy:
            scraper.scrape('test', self.last_week_time, self.current_time, '')
            self.assert_scrape_calls(scrape_spy, '')

        dates = self.generate_dates(deltas)
        mock_write.assert_has_calls([
            call(f'posts/test/{dates[0]}', 't3_test0', f'test title\n\n\ntest contents')
        ])

    if __name__ == '__main__':
        unittest.main()
